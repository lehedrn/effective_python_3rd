from unittest import TestCase, main

def sum_squares(values):
    cumulative = 0
    for value in values:
        cumulative += value**2
        yield cumulative

class HelperTestCase(TestCase):
    def verify_complex_case(self, values, expected):
        expect_it = iter(expected)
        found_it = iter(sum_squares(values))
        test_it = zip(expect_it, found_it, strict=True)

        for i, (expect, found) in enumerate(test_it):
            if found != expect:
                self.fail(f"Index {i} is wrong: {found} != {expect}")

    def test_too_short(self):
        values = [1.1, 2.2]
        expected = [1.1**2]
        self.verify_complex_case(values, expected)

    def test_too_long(self):
        values = [1.1, 2.2]
        expected = [
            1.1**2,
            1.1**2 + 2.2**2,
            0,  # Value doesn't matter
        ]
        self.verify_complex_case(values, expected)

    def test_wrong_results(self):
        values = [1.1, 2.2, 3.3]
        expected = [
            1.1**2,
            1.1**2 + 2.2**2,
            1.1**2 + 2.2**2 + 3.3**2 + 4.4**2,
        ]
        self.verify_complex_case(values, expected)

if __name__ == "__main__":
    main()