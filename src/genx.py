import pandas as pd


def main() -> None:
    """The entry point of a program."""
    genx_df = pd.read_csv('genx_sample.csv', header=None)
    print(genx_df)


if __name__ == '__main__':
    main()
