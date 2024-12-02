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

    # 데이터 추출
    data = []
    for line in lsfit_input_lines:
        if line.strip():
            parts = line.split()
            index, *parameter, value, increment = parts
            if index.isdigit() and parameter[-2] == 'part':
                index = int(index)
                name = " ".join(parameter[:-3])
                position_str = " ".join(parameter[-3:])
                position = (int(position_str[0]), int(position_str[-1]))
                layer = layers_manger.get_layer(position)
                layer.substance

                value = float(value)
                increment = float(increment)
            

        else:
            data.append(line)

    print(data)


    header: str = '''Parameter and refinement control file produced by  program LSFIT
DBI G/N Text for X-axis(A20) Text for Y-axis(A20) REP       
I   N   z  [\\AA]             log(|FT\\{Int\\cdotq_{   1
'''

    tail: str = '''Parameter Variation pattern  /  selected files :  1111
0        1         2         3         4         5         6         7         
1234567890123456789012345678901234567890123456789012345678901234567890123456789
'''
    lsfit_lines: list[str] = []
    index = 1
    
    return
    if False:
        parameter = row['parameter']
        value = row['value']
        fit = row['fit']
        min_value = row['min']
        max_value = row['max']

        if pd.notna(parameter):  # NaN이 아닌 경우만 처리
            increment = 0.0  # fit이 False인 경우 increment는 0으로 설정
            if fit:
                # fit이 True인 경우 increment를 적절히 설정 (예: 값의 10%로 설정)
                increment = (max_value - min_value) * 0.1

            lsfit_lines.append(f"{index:2d} {parameter:<30} {value:15.6e} {increment:15.6e}")
            index += 1
    
    return header + '\n'.join(lsfit_lines) + tail


def main() -> None:
    """The entry point of a program."""

    genx_file: str = 'genx_sample.csv'
    lsfit_file: str = 'lsfit_sample.con'

    genx_df = read_genx_file(genx_file).dropna()
    layers_manger = genx_df_to_layer_manager(genx_df)

    # 결과 출력
    print("All layers sorted by position:")
    for layer in layers_manger.list_layers():
        print(layer)

    # lsfit_df = read_lsfit_file(lsfit_file)

    # print(genx_df)


if __name__ == '__main__':
    main()
