import React from 'react'; // React 라이브러리를 가져옵니다.
import { TouchableOpacity, Text, StyleSheet, StyleProp, ViewStyle, TextStyle, View } from 'react-native'; // 사용할 React Native 기본 컴포넌트들을 가져옵니다.

// 버튼 컴포넌트가 외부로부터 전달받을 수 있는 속성(Props)들의 타입을 정의합니다.
interface CustomButtonProps {
  title: string; // 버튼 내부에 표시될 메인 텍스트입니다. (필수)
  onPress: () => void; // 버튼을 터치했을 때 실행될 함수입니다. (필수)
  style?: StyleProp<ViewStyle>; // 버튼의 컨테이너(외부 형태)에 추가로 적용할 스타일입니다. (선택)
  textStyle?: StyleProp<TextStyle>; // 버튼 내부 텍스트에 추가로 적용할 스타일입니다. (선택)
  color?: string; // 버튼의 기본 배경색입니다. (선택, 기본값 있음)
  disabled?: boolean; // 버튼 비활성화 여부를 결정하는 상태값입니다. API 통신 중 다중 클릭을 방지합니다. (선택)
  children?: React.ReactNode; // 버튼 내부에 텍스트 외에 추가할 컴포넌트(예: ActivityIndicator 로딩 스피너)입니다. (선택)
}

// CustomButton 함수형 컴포넌트를 선언합니다. 구조 분해 할당으로 Props를 바로 받아옵니다.
const CustomButton: React.FC<CustomButtonProps> = ({ 
  title, 
  onPress, 
  style, 
  textStyle, 
  color = '#1E90FF', // 색상이 전달되지 않으면 기본값으로 파란색(#1E90FF)을 사용합니다.
  disabled = false, // 비활성화 여부가 전달되지 않으면 기본적으로 활성화 상태(false)로 둡니다.
  children // 내부에 삽입될 자식 컴포넌트들을 받습니다.
}) => {
  return (
    // TouchableOpacity: 터치 시 투명도가 깜빡이며 클릭 피드백을 주는 기본 버튼 컨테이너입니다.
    <TouchableOpacity 
      style={[
        styles.button, // 기본 버튼 형태 스타일을 적용합니다.
        { backgroundColor: disabled ? '#BDC3C7' : color }, // disabled가 true면 회색(#BDC3C7)으로, 아니면 지정된 색상으로 배경을 덮어씁니다.
        style // 외부에서 추가로 넘겨받은 커스텀 스타일을 마지막에 덮어씌웁니다.
      ]} 
      onPress={onPress} // 터치 이벤트를 연결합니다.
      disabled={disabled} // true일 경우 React Native 자체적으로 터치 이벤트를 완전히 차단합니다.
    >
      {/* 텍스트와 로딩 스피너(children)를 가로로 나란히 배치하기 위한 내부 컨테이너입니다. */}
      <View style={styles.contentContainer}>
        {/* 버튼의 메인 텍스트를 렌더링합니다. */}
        <Text style={[styles.buttonText, textStyle]}>{title}</Text>
        {/* 만약 외부에서 전달된 자식 요소(로딩 스피너 등)가 있다면 텍스트 옆에 렌더링합니다. */}
        {children}
      </View>
    </TouchableOpacity>
  );
};

// 컴포넌트의 스타일을 정의하는 객체입니다.
const styles = StyleSheet.create({
  button: {
    borderRadius: 15, // 버튼의 모서리를 둥글게(15px) 깎아 부드러운 느낌을 줍니다.
    paddingVertical: 12, // 버튼 내부의 위아래 여백을 12px 줍니다.
    paddingHorizontal: 20, // 버튼 내부의 좌우 여백을 20px 줍니다.
    alignItems: 'center', // 컨테이너 내부의 자식들을 가로 중앙에 정렬합니다.
    justifyContent: 'center', // 컨테이너 내부의 자식들을 세로 중앙에 정렬합니다.
    shadowColor: '#000', // 그림자의 색상을 검은색으로 설정합니다. (iOS 전용)
    shadowOffset: {
      width: 0, // 그림자를 가로로는 이동시키지 않습니다.
      height: 2, // 그림자를 아래쪽으로 2px 내려 입체감을 줍니다.
    },
    shadowOpacity: 0.1, // 그림자의 투명도를 10%로 설정하여 은은하게 만듭니다.
    shadowRadius: 3.84, // 그림자가 퍼지는 반경을 설정합니다.
    elevation: 5, // 안드로이드 기기에서 그림자(Z축 깊이) 효과를 주기 위해 고도 5를 설정합니다.
  },
  contentContainer: {
    flexDirection: 'row', // 내부 요소(텍스트와 스피너)를 가로(행) 방향으로 나란히 배치합니다.
    alignItems: 'center', // 가로 방향 배치 시 세로축 기준 중앙 정렬합니다.
    justifyContent: 'center', // 가로 방향 배치 시 가로축 기준 중앙 정렬합니다.
  },
  buttonText: {
    color: '#FFFFFF', // 텍스트 색상을 흰색으로 설정합니다.
    fontSize: 16, // 텍스트 크기를 16px로 설정합니다.
    fontWeight: 'bold', // 텍스트 굵기를 굵게(bold) 설정하여 가독성을 높입니다.
  },
});

export default CustomButton; // 다른 파일에서 이 버튼을 사용할 수 있도록 내보냅니다.