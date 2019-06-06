import time
import unittest

class TimeLoggingTestResult(unittest.TextTestResult):

    def startTest(self, test):
        self._started_at = time.time()
        super().startTest(test)

    def addSuccess(self, test):
        elapsed = time.time() - self._started_at
        name = self.getDescription(test)
        self.stream.write(f"\n{name} ({elapsed:.03}s) ... OK")


if __name__ == '__main__':
    loader = unittest.TestLoader()
    tests = loader.discover('.')
    test_runner = unittest.TextTestRunner(resultclass=TimeLoggingTestResult)
    test_runner.run(tests)
