// React 라이브러리를 가져옵니다.
import React from 'react'; 
// React Native에서 화면을 구성하는 뷰, 스타일 시트, 그리고 타입스크립트용 스타일 타입을 가져옵니다.
import { View, StyleSheet, StyleProp, ViewStyle } from 'react-native'; 

// SoftCard 컴포넌트가 외부로부터 받을 속성(Props)들의 타입을 정의합니다.
interface SoftCardProps {
  // 카드 내부에 들어갈 모든 형태의 React 자식 요소들(텍스트, 버튼, 뷰 등)을 의미합니다. (필수)
  children: React.ReactNode; 
  // 카드의 기본 스타일 외에 여백이나 크기 등을 추가로 조절할 수 있도록 외부에서 스타일을 받습니다. (선택)
  style?: StyleProp<ViewStyle>; 
}

// 함수형 컴포넌트 SoftCard를 선언하고, children과 style을 Props로 구조 분해 할당하여 받습니다.
const SoftCard: React.FC<SoftCardProps> = ({ children, style }) => {
  // 기본 card 스타일을 적용한 View 컨테이너에 외부에서 넘겨받은 커스텀 style을 병합하여 자식 요소들을 감싸 반환합니다.
  return <View style={[styles.card, style]}>{children}</View>; 
};

// SoftCard에 적용될 고정적인 디자인 스타일을 정의합니다.
const styles = StyleSheet.create({
  card: {
    backgroundColor: '#FFFFFF', // 카드의 배경색을 순백색으로 설정하여 앱 배경(#F3F4F6)과 대비되게 합니다.
    borderRadius: 15, // 카드의 네 모서리를 15px 둥글게 처리하여 부드러운 인상을 줍니다.
    padding: 20, // 카드 테두리와 내부 콘텐츠 사이의 안쪽 여백을 20px로 설정합니다.
    marginVertical: 10, // 카드의 위아래 바깥 여백을 10px로 설정하여 다른 요소와 간격을 띄웁니다.
    
    // iOS 전용 그림자 설정
    shadowColor: '#000', // 그림자 색상을 검은색으로 설정합니다.
    shadowOffset: {
      width: 0, // 그림자를 가로로는 이동시키지 않습니다.
      height: 2, // 그림자를 아래쪽으로 2px 내려 입체감을 부여합니다.
    },
    shadowOpacity: 0.1, // 그림자의 투명도를 10%로 아주 옅게 설정하여 이름 그대로 'Soft'한 느낌을 살립니다.
    shadowRadius: 3.84, // 그림자의 퍼짐 정도를 설정합니다.
    
    // 안드로이드 전용 그림자(고도) 설정
    elevation: 5, // 안드로이드 기기에서 카드가 바닥에서 5만큼 떠 있는 듯한 입체감을 줍니다.
  },
});

// 다른 화면이나 컴포넌트에서 이 SoftCard를 가져다 쓸 수 있도록 기본 모듈로 내보냅니다.
export default SoftCard;