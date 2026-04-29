# Python Standard Library
from haversine import haversine
# Third-party Libraries
from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    page_size = 15


def calculate_km_between_two_points(initial_point: tuple, target_point: tuple):
    """
    Calculate the distance in kilometers between two geographical points.

    Parameters:
    initial_point (tuple): A tuple representing the initial
                           point with (latitude, longitude).
    target_point (tuple): A tuple representing the target
                          point with (latitude, longitude).

    Returns:
    float: The distance between the initial and target points
           in kilometers, rounded to 1 decimal place.
    """

    return round(haversine(initial_point, target_point), 1)
