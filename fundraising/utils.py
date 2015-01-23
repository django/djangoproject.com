from random import random


def shuffle_donations(donations):
    """
    Randomize the given list of donations but in a way that big donations
    have a bigger chance to be near the top (weighted random).
    """
    def keyfunc(donation):
        return float(donation.donated_amount) * random()
    return sorted(donations, key=keyfunc, reverse=True)
