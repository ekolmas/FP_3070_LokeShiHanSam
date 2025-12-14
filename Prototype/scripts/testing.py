import sys

def testingMethod():
    if len(sys.argv) < 2:
        print("Missing argument", file=sys.stderr)
        sys.exit(1)

    # Test if parameter from nodeJS is received
    testingParam = sys.argv[1]
    print(f"{testingParam} sent to python")

    print("Python script completed successfully")

if __name__ == "__main__":
    testingMethod()
