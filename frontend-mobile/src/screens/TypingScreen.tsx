import React, { useState, useRef, useMemo } from 'react'; // React 훅 임포트
import { View, Text, TextInput, StyleSheet, ScrollView, Alert, Dimensions } from 'react-native'; // 기본 컴포넌트 및 기기 크기 임포트
import { useRoute } from '@react-navigation/native'; // 네비게이션 파라미터 수신을 위해 필요
import SoftCard from '../components/SoftCard'; // 공통 카드 디자인 컴포넌트

// 기본 학습 지문 (파라미터가 없을 때 노출)
const DEFAULT_TEXT = "지혜로운 자는 경험에서 배우고, 더 지혜로운 자는 타인의 경험에서 배운다.";

export default function TypingScreen() {
  const route = useRoute();
  const textInputRef = useRef<TextInput>(null);
  
  // [기획 반영] 이전 화면(HomeScreen 등)에서 전달된 학습 텍스트가 있으면 그것을 연습 지문으로 사용
  const originalText = (route.params as any)?.learningText || DEFAULT_TEXT;
  
  const [typedText, setTypedText] = useState(''); // 사용자가 현재 입력한 텍스트 상태

  // [성능 최적화] 타이핑할 때마다 글자 색상을 계산하여 렌더링
  // useMemo를 사용하여 불필요한 계산을 줄이고 렌더링 성능 확보
  const highlightedText = useMemo(() => {
    return originalText.split('').map((char: string, index: number) => {
      const typedChar = typedText[index];
      let color = '#BDC3C7'; // 아직 입력하지 않은 글자 (연한 회색)

      if (typedChar !== undefined) {
        // 입력된 글자가 원본과 일치하면 초록색, 틀리면 빨간색
        color = typedChar === char ? '#2ECC71' : '#E74C3C';
      }
      
      return (
        <Text key={index} style={{ color, fontSize: 18, fontWeight: '500' }}>
          {char}
        </Text>
      );
    });
  }, [typedText, originalText]);

  // 입력 값이 변경될 때마다 호출되는 함수
  const handleTextChange = (text: string) => {
    // 원본 텍스트 길이를 초과하여 입력하지 못하도록 방지
    if (text.length <= originalText.length) {
      setTypedText(text);
    }

    // [완료 로직] 모든 텍스트를 다 쳤을 때 결과 알림
    if (text.length === originalText.length) {
      const isCorrect = text === originalText;
      if (isCorrect) {
        Alert.alert('🎉 암기 완료!', '완벽하게 타이핑했습니다. 문장이 머릿속에 저장되었습니다!');
      } else {
        Alert.alert('⚠️ 확인 필요', '틀린 부분이 있습니다. 빨간색 글자를 확인해보세요.');
      }
    }
  };

  // 정확도 계산 (%)
  const accuracy = useMemo(() => {
    if (typedText.length === 0) return 0;
    let correctCount = 0;
    for (let i = 0; i < typedText.length; i++) {
      if (typedText[i] === originalText[i]) correctCount++;
    }
    return Math.floor((correctCount / typedText.length) * 100);
  }, [typedText, originalText]);

  return (
    <ScrollView style={styles.container} contentContainerStyle={{ paddingBottom: 40 }}>
      <Text style={styles.title}>✍️ 암기 문장 타이핑 연습</Text>

      {/* 진행도 표시 영역 */}
      <View style={styles.statusContainer}>
        <Text style={styles.statusText}>진행률: {Math.floor((typedText.length / originalText.length) * 100)}%</Text>
        <Text style={[styles.statusText, { color: accuracy > 90 ? '#2ECC71' : '#E74C3C' }]}>정확도: {accuracy}%</Text>
      </View>

      <SoftCard style={styles.card}>
        <Text style={styles.label}>📖 암기할 문장</Text>
        <View style={styles.originalTextContainer}>
          {highlightedText}
        </View>
      </SoftCard>

      <SoftCard style={styles.card}>
        <Text style={styles.label}>⌨️ 따라 쓰기</Text>
        <TextInput
          ref={textInputRef}
          style={styles.textInput}
          placeholder="위 문장을 보며 정확하게 입력하세요..."
          multiline
          textAlignVertical="top"
          autoCapitalize="none"
          autoCorrect={false}
          value={typedText}
          onChangeText={handleTextChange}
          spellCheck={false} // 빨간 밑줄 방지
        />
      </SoftCard>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F3F4F6', padding: 20 },
  title: { fontSize: 26, fontWeight: 'bold', marginBottom: 20, textAlign: 'center', color: '#2C3E50' },
  statusContainer: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 15, paddingHorizontal: 5 },
  statusText: { fontSize: 14, fontWeight: '600', color: '#7F8C8D' },
  card: { marginBottom: 20, padding: 15 },
  label: { fontSize: 16, fontWeight: 'bold', marginBottom: 10, color: '#34495E' },
  originalTextContainer: {
    padding: 15,
    borderRadius: 12,
    backgroundColor: '#FFFFFF',
    minHeight: 100,
    flexDirection: 'row',
    flexWrap: 'wrap',
    borderWidth: 1,
    borderColor: '#ECF0F1',
  },
  textInput: {
    minHeight: 120,
    fontSize: 18,
    lineHeight: 26,
    color: '#2C3E50',
    padding: 10,
  },
});