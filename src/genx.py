import re

import pandas as pd

from src.layer import Layer, LayerManager


def read_genx_file(genx_file: str) -> pd.DataFrame:
    genx_df = pd.read_csv(genx_file, header=None)
    genx_df.columns = ['parameter', 'value', 'fit', 'min', 'max']
    return genx_df

def genx_df_to_layer_manager(genx_df: pd.DataFrame) -> LayerManager:

    genx_df = genx_df[~genx_df['parameter'].str.startswith('inst')]
    layer_data: dict[str: dict[str, float]] = {}

    for index in reversed(genx_df.index):
        row = genx_df.loc[index]
        parameter = row['parameter']
        substance, feature = parameter.split('.')
        value = row['value']

        if substance not in layer_data:
            layer_data[substance] = {}
        layer_data[substance][feature] = value

    positions = [(1, i + 1) for i in range(len(layer_data))]
    # LayerManager 생성
    manager = LayerManager()
    for i, (substance, features) in enumerate(layer_data.items()):
        layer = Layer(substance, positions[i], features)
        manager.set_layer(positions[i], layer)

    return manager

def read_lsfit_file(lsfit_file: str) -> pd.DataFrame:
    # 파일 읽기
    with open(lsfit_file, 'r', encoding='utf-8') as file:
        # "### name of parameter............."가 나올 때까지 스킵
        while True:
            line = next(file, None)
            if line is None:
                raise ValueError("File does not contain the expected header.")
            if "### name of parameter............." in line:
                break
        lines = file.readlines()

    # 데이터 추출
    data = []
    for line in lines:

        # 빈줄 제외
        if not line.strip():
            continue
        parts = line.split()
        index, *parameter, value, increment = parts

        # 줄이 숫자로 시작하지 않으면 종료
        if not index.isdigit():
            break
        if parameter[-2] != 'part':
            continue
        index = int(index)
        name = " ".join(parameter[:-3])
        position = " ".join(parameter[-3:])
        value = float(value)
        increment = float(increment)

        data.append([index, name, position, value, increment])

    return pd.DataFrame(data, columns=['Index', 'Name', 'Position', 'Value', 'Increment'])


def convert_genx_to_lsfit(layers_manger: LayerManager, lsfit_input: str, lsfit_output: str) -> None:

    with open(lsfit_input, 'r', encoding='utf-8') as file:
        # "### name of parameter............."가 나올 때까지 스킵
        while True:
            line = next(file, None)
            if line is None:
                raise ValueError("File does not contain the expected header.")
            if "### name of parameter............." in line:
                break
        lsfit_input_lines = file.readlines()

    def modify_line(line: str) -> None | str:
        if not line.strip():
            return line
        parts = line.split()
        if not parts[0].isdigit():
            return None
        index, *parameter, value, _ = parts
        if not index.isdigit() or parameter[-2] != 'part':
            return line
        position_str = " ".join(parameter[-3:])
        position = (int(position_str[0]), int(position_str[-1]))
        if position[0] == 0:
            return line
        name = " ".join(parameter[:-3])
        layer = layers_manger.get_layer(position)

        value: str | None = None
        match name:
            case "disp / n*b layer":
                value = None
            case "di_nb/beta layer":
                value = None
            case "sigma layer in A":
                value = layer.features['setSigma']
            case "layer thickness":
                value = layer.features['setD']
            case _:
                raise ValueError(f'wrong feature name: ({name})')

        formatted_value = "???" if value is None else f'{value:.6e}'
        new_line = re.sub(r'\d+\.\d+', formatted_value, line, count=1)
        return new_line

    # 데이터 추출
    lsfit_lines = []
    for line in lsfit_input_lines:
        new_line = modify_line(line)
        if new_line is None:
            break
        lsfit_lines.append(new_line)

    header: str = '''Parameter and refinement control file produced by  program LSFIT
DBI G/N Text for X-axis(A20) Text for Y-axis(A20) REP       
I   N   z  [\\AA]             log(|FT\\{Int\\cdotq_{   1
'''

    tail: str = '''Parameter Variation pattern  /  selected files :  1111
0        1         2         3         4         5         6         7         
1234567890123456789012345678901234567890123456789012345678901234567890123456789
'''

    return header + ''.join(lsfit_lines) + tail


def main() -> None:
    """The entry point of a program."""

    genx_file: str = 'genx_sample.csv'
    lsfit_file: str = 'lsfit_sample.con'

    genx_df = read_genx_file(genx_file).dropna()
    layers_manger = genx_df_to_layer_manager(genx_df)

    new_lsfit = convert_genx_to_lsfit(layers_manger, lsfit_file, None)

    new_lsfit_file = 'new_lsfit_sample.con'
    with open(new_lsfit_file, 'w', encoding='utf-8') as f:
        f.write(new_lsfit)


if __name__ == '__main__':
    main()
