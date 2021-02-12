import pytest
import numpy as np

from afaligner.c_dtwbd_wrapper import c_FastDTWBD


def test_perfect_match():
    s = np.arange(10, dtype='float64').reshape(-1,1)
    t = np.arange(10, dtype='float64').reshape(-1,1)
    distance, path = c_FastDTWBD(s, t, skip_penalty=100, radius=10)
    assert distance == pytest.approx(0.0)
    np.testing.assert_equal(path[:,0], np.arange(10))
    np.testing.assert_equal(path[:,1], np.arange(10))


def test_no_match():
    s = np.arange(10, dtype='float64').reshape(-1,1)
    t = np.arange(10, 20, dtype='float64').reshape(-1,1)
    distance, path = c_FastDTWBD(s, t, skip_penalty=0, radius=10)
    assert distance == pytest.approx(0.0)
    assert len(path) == 0


def test_all_to_one_match():
    s = 5 * np.ones(10, dtype='float64').reshape(-1,1)
    t = np.array([[5]], dtype='float64')
    distance, path = c_FastDTWBD(s, t, skip_penalty=1, radius=10)
    assert distance == pytest.approx(0.0)
    assert len(path) == 10
    np.testing.assert_equal(path[:,0], np.arange(10))
    np.testing.assert_equal(path[:,1], np.zeros(10))


def test_perfect_match_in_the_middle():
    skip_penalty = 0.5
    s = np.arange(20, 80, dtype='float64').reshape(-1,1)
    t = np.arange(100, dtype='float64').reshape(-1,1)
    distance, path = c_FastDTWBD(s, t, skip_penalty=skip_penalty, radius=100)
    assert distance == pytest.approx((len(t) - len(s)) * skip_penalty)
    assert len(path) == len(s)
    np.testing.assert_equal(path[:,0], np.arange(60))
    np.testing.assert_equal(path[:,1], np.arange(20, 80))


def test_allocate_large_matrix():
    s = np.arange(100000, dtype='float64').reshape(-1,1)
    t = np.arange(100000, dtype='float64').reshape(-1,1)
    c_FastDTWBD(s, t, skip_penalty=0.5, radius=100)