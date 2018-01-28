def intersection(a, b):
    """
    Computes intersection between lines a and b.
    Returns None if no intersection is found.
    """
    # Based on https://stackoverflow.com/questions/20677795/how-do-i-compute-the-intersection-point-of-two-lines-in-python#20679579
    # Added range check.

    def line(l):
        p1, p2 = l
        A = (p1[1] - p2[1])
        B = (p2[0] - p1[0])
        C = (p1[0]*p2[1] - p2[0]*p1[1])
        return A, B, -C

    def xrange(l):
        nrs = (l[0][0], l[1][0])
        return min(nrs), max(nrs)
    def yrange(l):
        nrs = (l[0][1], l[1][1])
        return min(nrs), max(nrs)

    def ranges_overlap(a,b):
       return (a[0] <= b[0] and a[1] >= b[0]) or (b[0] <= a[0] and b[1] >= a[0])

    L1 = line(a)
    L2 = line(b)

    D  = L1[0] * L2[1] - L1[1] * L2[0]
    Dx = L1[2] * L2[1] - L1[1] * L2[2]
    Dy = L1[0] * L2[2] - L1[2] * L2[0]

    if D != 0:
        x = Dx / D
        y = Dy / D

        if ranges_overlap(xrange(a), xrange(b)) and ranges_overlap(yrange(a), yrange(b)):
            return x,y
        else:
            return None
    else:
        return None
