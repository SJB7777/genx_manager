class Layer:
    def __init__(self, substance: str, position: tuple[int, int], features: dict[str, float]):
        self.substance = substance
        self.position = position
        self.features = features  # 물질의 특성을 저장하는 딕셔너리

    def add_feature(self, feature_name: str, value: float):
        """특징을 추가하거나 수정하는 메서드"""
        self.features[feature_name] = value

    def update_features(self, new_features: dict[str, float]):
        """기존 특성을 업데이트하는 메서드"""
        self.features.update(new_features)


    def __repr__(self):
        return f"Layer(substance={self.substance}, position={self.position}, features={self.features})"

    def __lt__(self, other):
        """Layer 객체의 포지션을 기준으로 비교"""
        return self.position < other.position


class LayerManager:
    def __init__(self):
        self.layers: dict[tuple[int, int], Layer] = {}

    def add_feature(self, position: tuple[int, int], feature: str, value: float):
        self.layers[position].add_feature(feature, value)

    def set_layer(self, position: tuple[int, int], layer: Layer):
        self.layers[position] = layer

    def get_layer(self, position: tuple[int, int]) -> Layer | None:
        """position을 기준으로 Layer를 반환"""
        return self.layers.get(position, None)

    def remove_layer(self, position: tuple[int, int]):
        """특정 포지션의 레이어를 제거"""
        if position in self.layers:
            del self.layers[position]
        else:
            raise ValueError(f"Position {position} does not exist.")
    
    def update_features(self, position: tuple[int, int], new_features: dict[str, float]):
        """기존 레이어의 특성을 업데이트"""
        if position in self.layers:
            self.layers[position].update_features(new_features)
        else:
            raise ValueError(f"Position {position} does not exist.")

    def list_layers(self):
        """Layer를 position 기준으로 정렬하여 반환"""
        return sorted(self.layers.values(), key=lambda layer: layer.position)


# 예시 사용법
if __name__ == "__main__":
    # 예시 데이터프레임 (genx_df)
    import pandas as pd
    data = {
        'parameter': ['inst.density', 'inst.conductivity', 'material1.density', 'material1.conductivity'],
        'value': [1.2, 0.5, 2.0, 1.0]
    }
    genx_df = pd.DataFrame(data)

    # LayerManager 생성
    manager = LayerManager()
    current_sub_position = 1  # 현재 위치

    # genx_df에서 LayerManager로 데이터 처리
    for _, row in genx_df.iterrows():
        parameter = row['parameter']
        substance, feature_name = parameter.split('.')
        value = row['value']

        if substance == 'inst':
            continue  # 'inst'는 무시

        # substance가 새로 등장하면 새로운 Layer를 추가하고, 이미 있으면 해당 Layer에 feature를 추가
        manager.set_layer(substance, (1, current_sub_position), feature_name, value)
        current_sub_position += 1

    # 결과 출력
    print("All layers sorted by position:")
    for layer in manager.list_layers():
        print(layer)

    # 특정 position에 해당하는 Layer 조회
    print("\nLayer at position (1, 2):")
    print(manager.get_layer((1, 2)))
