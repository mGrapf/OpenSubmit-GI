'''
Test cases for 'GET' views and actions available for admins.
They include all cases for teachers through inheritance.
'''

from .cases import SubmitAdminTestCase
from .helpers.user import create_user, get_student_dict
from .helpers.testmachine import create_test_machine


class Admin(SubmitAdminTestCase):
    def test_merge_users_view(self):
        user1 = create_user(get_student_dict(1))
        user2 = create_user(get_student_dict(2))
        response = self.c.get('/mergeusers/{0}/{1}/'.format(user1.pk, user2.pk))
        self.assertEqual(response.status_code, 200)

    def test_merge_users_action(self):
        user1 = create_user(get_student_dict(1))
        user2 = create_user(get_student_dict(2))
        response = self.c.post('/mergeusers/{0}/{1}/'.format(user1.pk, user2.pk))
        self.assertEqual(response.status_code, 302)

    def test_test_machine_list_view(self):
        # one machine given
        create_test_machine('127.0.0.1')
        response = self.c.get('/teacher/opensubmit/testmachine/')
        self.assertEqual(response.status_code, 200)

    def test_can_use_admin_backend(self):
        response = self.c.get('/teacher/auth/user/')
        self.assertEqual(response.status_code, 200)
