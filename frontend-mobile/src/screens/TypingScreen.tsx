// React 라이브러리에서 상태 관리와 성능 최적화를 위한 훅을 가져옵니다.
import React, { useState, useRef, useMemo } from 'react'; 
// React Native의 핵심 UI 컴포넌트들을 임포트합니다.
import { View, Text, TextInput, StyleSheet, ScrollView, Alert } from 'react-native'; 
// 이전 스크린에서 넘겨준 학습 데이터를 받기 위해 네비게이션 훅을 사용합니다.
import { useRoute } from '@react-navigation/native'; 
// UI 통일성을 유지하기 위해 공통 SoftCard 컴포넌트를 불러옵니다.
import SoftCard from '../components/SoftCard'; 

// 파라미터로 넘어온 텍스트가 없을 경우 기본으로 제공될 연습 문장입니다.
const DEFAULT_TEXT = "지혜로운 자는 경험에서 배우고, 더 지혜로운 자는 타인의 경험에서 배운다.";

export default function TypingScreen() {
  // 현재 라우트 정보를 가져옵니다.
  const route = useRoute();
  // TextInput 컴포넌트를 직접 제어하기 위한 참조 변수입니다.
  const textInputRef = useRef<TextInput>(null);
  
  // 이전 화면에서 'learningText'를 전달받았다면 그것을 쓰고, 없으면 기본 문장을 씁니다.
  const originalText = (route.params as any)?.learningText || DEFAULT_TEXT;
  
  // 사용자가 입력하고 있는 텍스트를 저장하는 상태입니다.
  const [typedText, setTypedText] = useState(''); 

  // [복구됨] 타이핑할 때마다 원본 글자와 비교하여 색상을 입히는 핵심 로직입니다.
  // useMemo를 사용해 typedText가 바뀔 때만 연산하도록 최적화했습니다.
  const highlightedText = useMemo(() => {
    // 원본 텍스트를 한 글자씩 쪼개어 배열로 만든 뒤 검사합니다.
    return originalText.split('').map((char: string, index: number) => {
      // 사용자가 현재 인덱스에 입력한 글자를 가져옵니다.
      const typedChar = typedText[index];
      // 기본 색상은 아직 입력하지 않은 글자를 의미하는 연한 회색입니다.
      let color = '#BDC3C7'; 

      // 사용자가 이 자리의 글자를 입력했다면
      if (typedChar !== undefined) {
        // 일치하면 연두색(#2ECC71), 틀리면 빨간색(#E74C3C)을 부여합니다.
        color = typedChar === char ? '#2ECC71' : '#E74C3C';
      }
      
      // 색상이 적용된 Text 컴포넌트를 반환합니다.
      return (
        <Text key={index} style={{ color, fontSize: 18, fontWeight: '500' }}>
          {char}
        </Text>
      );
    });
  }, [typedText, originalText]); // 사용자의 입력이 변할 때만 리렌더링됩니다.

  // [복구됨] 사용자가 글자를 입력할 때마다 실행되는 핸들러입니다.
  const handleTextChange = (text: string) => {
    // 원본 문장보다 길게 타자를 치는 것을 방지합니다.
    if (text.length <= originalText.length) {
      setTypedText(text); // 상태를 업데이트합니다.
    }

    // 목표 문장 끝까지 다 타이핑을 마쳤다면 결과를 판별합니다.
    if (text.length === originalText.length) {
      // 입력 문장과 원본 문장이 100% 동일한지 확인합니다.
      const isCorrect = text === originalText;
      if (isCorrect) {
        // 오타가 하나도 없으면 성공 알림을 띄웁니다.
        Alert.alert('🎉 암기 완료!', '완벽하게 타이핑했습니다. 문장이 머릿속에 저장되었습니다!');
      } else {
        // 오타가 있다면 빨간색 글자를 고치라고 알려줍니다.
        Alert.alert('⚠️ 확인 필요', '틀린 부분이 있습니다. 빨간색 글자를 확인해보세요.');
      }
    }
  };

  // [복구됨] 전체 글자 중 맞게 친 글자의 비율(정확도)을 계산합니다.
  const accuracy = useMemo(() => {
    // 아직 아무것도 안 쳤으면 정확도는 0%입니다.
    if (typedText.length === 0) return 0;
    let correctCount = 0; // 맞춘 글자 수 카운터
    // 입력한 길이만큼 반복문을 돌며 맞춘 개수를 셉니다.
    for (let i = 0; i < typedText.length; i++) {
      if (typedText[i] === originalText[i]) correctCount++;
    }
    // 퍼센티지로 변환하고 소수점은 내림 처리합니다.
    return Math.floor((correctCount / typedText.length) * 100);
  }, [typedText, originalText]);

  return (
    // 스크롤 뷰를 사용하되, 하단 플로팅 메뉴바(약 115px)에 가려지지 않도록 넉넉한 하단 여백을 줍니다.
    <ScrollView style={styles.container} contentContainerStyle={{ paddingBottom: 115 }}>
      {/* 화면 상단 타이틀 */}
      <Text style={styles.title}>✍️ 암기 문장 타이핑 연습</Text>

      {/* [복구됨] 현재 진행 상태(진행률, 정확도)를 보여주는 상단 바입니다. */}
      <View style={styles.statusContainer}>
        <Text style={styles.statusText}>진행률: {Math.floor((typedText.length / originalText.length) * 100)}%</Text>
        {/* 정확도가 90% 초과면 연두색, 이하면 빨간색으로 경고를 줍니다. */}
        <Text style={[styles.statusText, { color: accuracy > 90 ? '#2ECC71' : '#E74C3C' }]}>정확도: {accuracy}%</Text>
      </View>

      {/* 내가 보고 따라 쳐야 할, 색상이 동적으로 변하는 원본 텍스트 영역입니다. */}
      <SoftCard style={styles.card}>
        <Text style={styles.label}>📖 암기할 문장</Text>
        <View style={styles.originalTextContainer}>
          {/* useMemo로 계산해둔 색상 입힌 텍스트 배열을 출력합니다. */}
          {highlightedText}
        </View>
      </SoftCard>

      {/* 사용자가 실제로 글자를 입력하는 영역입니다. */}
      <SoftCard style={styles.card}>
        <Text style={styles.label}>⌨️ 따라 쓰기</Text>
        <TextInput
          ref={textInputRef} // 조작을 위한 참조 연결
          style={styles.textInput} // 입력창 기본 디자인
          placeholder="위 문장을 보며 정확하게 입력하세요..." // 비어있을 때 안내 문구
          multiline // 여러 줄 입력을 허용합니다.
          textAlignVertical="top" // 글자가 위에서부터 시작하도록 정렬합니다.
          autoCapitalize="none" // 자동 대문자 변환을 끕니다.
          autoCorrect={false} // 자동 완성 및 수정을 끕니다. (타자 연습이므로)
          value={typedText} // 현재 입력 상태값을 바인딩합니다.
          onChangeText={handleTextChange} // 글자가 변할 때마다 검사 함수를 부릅니다.
          spellCheck={false} // 빨간 밑줄(스펠체크)이 보이지 않게 합니다.
        />
      </SoftCard>
    </ScrollView>
  );
}

// 화면을 꾸미는 스타일 정의입니다.
const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F3F4F6', padding: 20 }, // 전체 배경은 연한 회색으로 통일합니다.
  title: { fontSize: 26, fontWeight: 'bold', marginBottom: 20, textAlign: 'center', color: '#2C3E50' }, // 상단 제목 스타일입니다.
  statusContainer: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 15, paddingHorizontal: 5 }, // 진행률과 정확도를 양쪽 끝으로 배치합니다.
  statusText: { fontSize: 14, fontWeight: '600', color: '#7F8C8D' }, // 상태 텍스트의 기본 회색입니다.
  card: { marginBottom: 20, padding: 15 }, // 카드 간의 간격과 안쪽 여백을 설정합니다.
  label: { fontSize: 16, fontWeight: 'bold', marginBottom: 10, color: '#34495E' }, // 카드 안의 작은 제목 스타일입니다.
  originalTextContainer: {
    padding: 15, // 안쪽 여백
    borderRadius: 12, // 둥근 모서리
    backgroundColor: '#FFFFFF', // 흰색 배경
    minHeight: 100, // 최소 높이 보장
    flexDirection: 'row', // 글자들이 가로로 배치되게 합니다.
    flexWrap: 'wrap', // 글자가 영역을 넘어가면 다음 줄로 넘깁니다.
    borderWidth: 1, // 얇은 테두리
    borderColor: '#ECF0F1', // 연한 테두리 색상
  },
  textInput: {
    minHeight: 120, // 입력창 최소 높이 보장
    fontSize: 18, // 큼직한 글씨 크기
    lineHeight: 26, // 줄 간격을 줘서 읽기 편하게 합니다.
    color: '#2C3E50', // 기본 텍스트 색상
    padding: 10, // 입력창 안쪽 여백
  },
});