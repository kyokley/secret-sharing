import unittest
import mock
import string
from secretsharing.sharing import (points_to_point,
                                   points_to_secret_int,
                                   SecretSharer)

class TestPointsToPoints(unittest.TestCase):
    def setUp(self):
        self.get_large_enough_prime_patcher = mock.patch('secretsharing.sharing.get_large_enough_prime')
        self.mock_get_large_enough_prime = self.get_large_enough_prime_patcher.start()

        self.modular_lagrange_interpolation_patcher = mock.patch('secretsharing.sharing.modular_lagrange_interpolation')
        self.mock_modular_lagrange_interpolation = self.modular_lagrange_interpolation_patcher.start()

        self.points = [(0, 1),
                       (1, 2),
                       (2, 3)]

    def tearDown(self):
        self.get_large_enough_prime_patcher.stop()
        self.modular_lagrange_interpolation_patcher.stop()

    def test_points_is_not_list(self):
        self.assertRaises(ValueError,
                          points_to_point,
                          'asdf',
                          10,
                          prime=None)
        self.assertFalse(self.mock_get_large_enough_prime.called)
        self.assertFalse(self.mock_modular_lagrange_interpolation.called)

    def test_point_not_tuple(self):
        self.points = [(0, 1),
                       'asdf',
                       (2, 3)]
        self.assertRaises(ValueError,
                          points_to_point,
                          self.points,
                          10,
                          prime=None)
        self.assertFalse(self.mock_get_large_enough_prime.called)
        self.assertFalse(self.mock_modular_lagrange_interpolation.called)

    def test_point_is_not_2_tuple(self):
        self.points = [(0, 1),
                       (1, 2, 3),
                       (2, 3)]
        self.assertRaises(ValueError,
                          points_to_point,
                          self.points,
                          10,
                          prime=None)
        self.assertFalse(self.mock_get_large_enough_prime.called)
        self.assertFalse(self.mock_modular_lagrange_interpolation.called)

    def test_point_contains_non_int_types1(self):
        self.points = [(0, 1),
                       ('asdf', 2),
                       (2, 3)]
        self.assertRaises(ValueError,
                          points_to_point,
                          self.points,
                          10,
                          prime=None)
        self.assertFalse(self.mock_get_large_enough_prime.called)
        self.assertFalse(self.mock_modular_lagrange_interpolation.called)

    def test_point_contains_non_int_types2(self):
        self.points = [(0, 1),
                       (2, 'asdf'),
                       (2, 3)]
        self.assertRaises(ValueError,
                          points_to_point,
                          self.points,
                          10,
                          prime=None)
        self.assertFalse(self.mock_get_large_enough_prime.called)
        self.assertFalse(self.mock_modular_lagrange_interpolation.called)

    def test_no_prime_found(self):
        self.mock_get_large_enough_prime.return_value = None
        self.assertRaises(ValueError,
                          points_to_point,
                          self.points,
                          10,
                          prime=None)
        self.mock_get_large_enough_prime.assert_called_once_with((1, 2, 3))
        self.assertFalse(self.mock_modular_lagrange_interpolation.called)

    def test_(self):
        expected = (10, self.mock_modular_lagrange_interpolation.return_value)
        actual = points_to_point(self.points, 10, prime=None)

        self.assertEqual(expected, actual)
        self.mock_get_large_enough_prime.assert_called_once_with((1, 2, 3))
        self.mock_modular_lagrange_interpolation.assert_called_once_with(10, self.points, self.mock_get_large_enough_prime.return_value)

class TestPointsToSecretInt(unittest.TestCase):
    def setUp(self):
        self.points_to_point_patcher = mock.patch('secretsharing.sharing.points_to_point')
        self.mock_points_to_point = self.points_to_point_patcher.start()
        self.mock_points_to_point.return_value = (1, 2)

        self.points = [(0, 1),
                       (1, 2),
                       (2, 3)]

    def tearDown(self):
        self.points_to_point_patcher.stop()

    def test_(self):
        expected = self.mock_points_to_point.return_value[1]
        actual = points_to_secret_int(self.points, prime=None)

        self.assertEqual(expected, actual)
        self.mock_points_to_point.assert_called_once_with(self.points,
                                                          0,
                                                          prime=None)

class TestRecoverShard(unittest.TestCase):
    def setUp(self):
        self.share_string_to_point_patcher = mock.patch('secretsharing.sharing.share_string_to_point')
        self.mock_share_string_to_point = self.share_string_to_point_patcher.start()
        self.mock_share_string_to_point.side_effect = [(0, 1),
                                                       (1, 2),
                                                       (2, 3)]

        self.points_to_point_patcher = mock.patch('secretsharing.sharing.points_to_point')
        self.mock_points_to_point = self.points_to_point_patcher.start()

        self.point_to_share_string_patcher = mock.patch('secretsharing.sharing.point_to_share_string')
        self.mock_point_to_share_string = self.point_to_share_string_patcher.start()

        self.charset = string.hexdigits[:16]

        self.shares = ['1-123',
                       '2-234',
                       '3-345',]
        self.index = 10

    def tearDown(self):
        self.share_string_to_point_patcher.stop()
        self.points_to_point_patcher.stop()
        self.point_to_share_string_patcher.stop()

    def test_(self):
        expected = self.mock_point_to_share_string.return_value
        actual = SecretSharer.recover_share(self.shares, self.index)

        self.assertEqual(expected, actual)
        self.mock_share_string_to_point.assert_has_calls([mock.call('1-123', self.charset),
                                                          mock.call('2-234', self.charset),
                                                          mock.call('3-345', self.charset),
                                                          ])
        self.mock_points_to_point.assert_called_once_with([(0, 1),
                                                           (1, 2),
                                                           (2, 3)], self.index)
        self.mock_point_to_share_string.assert_called_once_with(self.mock_points_to_point.return_value,
                                                                self.charset)
