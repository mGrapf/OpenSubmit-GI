from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Group, Permission
from opensubmit.models import Submission, Course, SubmissionFile

STUDENT_TUTORS_GROUP_NAME = "Student Tutors"
COURSE_OWNERS_GROUP_NAME = "Course Owners"

def check_permission_system():
    '''
        This methods makes sure that:

        1.) All neccessary user groups exist.
        2.) All these groups have the right database permissions assigned.
        3.) Tutors have backend rights.
        4.) Course owners have backend rights.
        5.) Students have no backend rights.

        The permission objects were already generated by the Django database initialization,
        so we can assume them to be given.

        This method is idempotent and does not touch manually assigned permissions.
    '''
    tutor_perms = ( "change_submission", "delete_submission",
                    "change_submissionfile", "delete_submissionfile" )
    owner_perms = ( "add_assignment", "change_assignment", "delete_assignment",
                    "add_grading", "change_grading",  "delete_grading",
                    "add_gradingscheme", "change_gradingscheme", "delete_gradingscheme",
                    "add_submission", "change_submission", "delete_submission",
                    "add_submissionfile", "change_submissionfile", "delete_submissionfile",
                    "add_course", "change_course", "delete_course", "add_testmachine",
                    "change_testmachine", "delete_testmachine" )

    # Give all tutor users staff rights and add them to the tutors permission group
    tutors = User.objects.filter(courses_tutoring__isnull=False)
    tutors.update(is_staff=True)
    # If the app crashes here, you may have duplicate group objects, which must be fixed manually in the DB.
    tutor_group, created = Group.objects.get_or_create(name=STUDENT_TUTORS_GROUP_NAME)
    # If the app crashes here, you may have duplicate permission objects, which must be fixed manually in the DB.
    tutor_group.permissions = [Permission.objects.get(codename=perm) for perm in tutor_perms]
    tutor_group.user_set.add(*tutors)
    tutor_group.save()

    # Give all course owner users staff rights and add them to the course owners permission group
    owners = User.objects.filter(courses__isnull=False)
    owners.update(is_staff=True)
    # If the app crashes here, you may have duplicate group objects, which must be fixed manually in the DB.
    owner_group, created = Group.objects.get_or_create(name=COURSE_OWNERS_GROUP_NAME)
    # If the app crashes here, you may have duplicate permission objects, which must be fixed manually in the DB.
    owner_group.permissions = [Permission.objects.get(codename=perm) for perm in owner_perms]
    owner_group.user_set.add(*owners)
    owner_group.save()

    # Make sure that pure students (no tutor, no course owner, no superuser) have no backend access at all
    pure_students = User.objects.filter(courses__isnull=True, courses_tutoring__isnull=True, is_superuser=False)
    pure_students.update(is_staff=False)

@receiver(post_save, sender=User)
def post_user_save(sender,instance, signal, created, **kwargs):
    """
        Make sure that all neccessary user groups exist and have the right permissions,
        directly after the auth system was installed. We detect this by waiting for the admin
        account creation here, which smells hacky.
        We need that automatism for the test database creation, people not calling the configure tool and similar cases.
    """
    if instance.is_staff and created:
        check_permission_system()

@receiver(post_save, sender=SubmissionFile)
def submissionfile_post_save(sender,instance, signal, created, **kwargs):
    '''
        Update MD5 field for newly uploaded files.
    '''
    if created:
        instance.md5 = instance.attachment_md5()
        instance.save()

@receiver(post_save, sender=Submission)
def submission_post_save(sender, instance, **kwargs):
    ''' Several sanity checks after we got a valid submission object.'''
    # Make the submitter an author
    if instance.submitter not in instance.authors.all():
        instance.authors.add(instance.submitter)
        instance.save()
    # Mark all existing submissions for this assignment by these authors as invalid.
    # This fixes a race condition with parallel new submissions in multiple browser windows by the same user.
    # Solving this as pre_save security exception does not work, since we have no instance with valid foreign keys to check there.
    # Considering that this runs also on tutor correction backend activities, it also serves as kind-of cleanup functionality
    # for multiplse submissions by the same students for the same assignment - however they got in here.
    if instance.state == instance.get_initial_state():
        for author in instance.authors.all():
            same_author_subm = User.objects.get(pk=author.pk).authored.all().exclude(pk=instance.pk).filter(assignment=instance.assignment)
            for subm in same_author_subm:
                subm.state = Submission.WITHDRAWN
                subm.save()

@receiver(post_save, sender=Course)
def course_post_save(sender, instance, **kwargs):
    '''
        After creating / modifying a course, make sure that only tutors and course owners have backend access rights.
        We do that here since tutor addition and removal ends up in a course modification signal.
    '''
    check_permission_system()