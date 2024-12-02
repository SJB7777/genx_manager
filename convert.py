import re
import pandas as pd


def read_lsfit_file(input_file):



    # 1. 텍스트 파일 읽
    with open(input_file, "r", encoding="utf-8") as file:
        lines = file.readlines()

        # 2. 필요한 데이터 추출
        # "### name of parameter" 이후 데이터만 추출
        start_index = next(i for i, line in enumerate(lines) if "### name of parameter" in line) + 1
        data_lines = lines[start_index:]

        # 3. 유효한 데이터만 필터링 (파라미터 ID로 시작하는 라인만 포함)
        pattern = re.compile(r"^\s*\d+\s")  # 숫자로 시작하는 줄만 추출
        filtered_lines = [line.strip() for line in data_lines if pattern.match(line)]

        # 4. 데이터를 DataFrame으로 변환
        # 정규식을 사용해 ID, 이름, 값, 증분으로 분리
        data = []
        for line in filtered_lines:
            match = re.match(r"^\s*(\d+)\s+([^\d]+?)\s+([-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?)\s+([-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?)?$", line)
            if match:
                param_id = match.group(1)  # ID
                param_name = match.group(2).strip()  # Parameter Name
                value = match.group(3)  # Value
                increment = match.group(4) if match.group(4) else None  # Increment (없을 수도 있음)
                data.append([param_id, param_name, value, increment])

    return pd.DataFrame(data, columns=["Parameter ID", "Parameter Name", "Value", "Increment"])



genx_file = "exe.csv"
lsfit_file = "ex.con"

genx_df = pd.read_csv(genx_file, header=None)
genx_df.columns = ['parameter', 'value', 'fit', 'min', 'max']
genx_df = genx_df.dropna()
filtered_df = genx_df[genx_df['parameter'].str.endswith(('.setD', '.setDens', '.setSigma'))]

matters = ['HfO2_1', 'SiO2_1', 'SiO2_2']

lsfit_df = read_lsfit_file(lsfit_file)
print(lsfit_df['Parameter ID'])
