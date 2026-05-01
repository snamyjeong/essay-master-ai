import React, { useState } from 'react';
import { View, Text, TextInput, ScrollView, StyleSheet, Alert, ActivityIndicator } from 'react-native';
import SoftCard from '../components/SoftCard';
import CustomButton from '../components/CustomButton';

export default function QuizScreen() {
  const [keywordAnswer, setKeywordAnswer] = useState('');
  const [essayAnswer, setEssayAnswer] = useState('');
  const [isEvaluating, setIsEvaluating] = useState(false);

  return (
    // [수정] ScrollView 하단 여백 추가
    <ScrollView style={styles.container} contentContainerStyle={{ paddingBottom: 110 }}>
      <SoftCard style={styles.sectionCard}>
        <Text style={styles.sectionTitle}>💡 키워드 퀴즈</Text>
        <Text style={styles.questionText}>Q1. 본문의 핵심 키워드는 무엇인가요?</Text>
        <View style={styles.answerInputContainer}>
          <TextInput style={styles.keywordInput} placeholder="정답..." value={keywordAnswer} onChangeText={setKeywordAnswer} />
          <CustomButton title="✔️ 채점" onPress={() => Alert.alert('채점 완료')} style={styles.scoreButton} />
        </View>
      </SoftCard>
      <SoftCard style={styles.sectionCard}>
        <Text style={styles.sectionTitle}>🚀 서술형 심화학습</Text>
        <Text style={styles.essayInputLabel}>서술형 답변을 입력하세요.</Text>
        <TextInput style={styles.essayInput} multiline value={essayAnswer} onChangeText={setEssayAnswer} />
        <CustomButton title={isEvaluating ? "평가 중..." : "📊 서술형 답안 평가"} onPress={() => {}} disabled={isEvaluating} />
      </SoftCard>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F3F4F6', padding: 20 },
  sectionCard: { marginBottom: 20, padding: 15 },
  sectionTitle: { fontSize: 22, fontWeight: 'bold', marginBottom: 15 },
  questionText: { fontSize: 17, marginBottom: 10 },
  answerInputContainer: { flexDirection: 'row' },
  keywordInput: { flex: 1, borderWidth: 1, borderColor: '#ddd', borderRadius: 8, padding: 10, marginRight: 10 },
  scoreButton: { minWidth: 80 },
  essayInputLabel: { fontSize: 16, marginBottom: 10 },
  essayInput: { minHeight: 150, borderWidth: 1, borderColor: '#ddd', borderRadius: 8, padding: 10, textAlignVertical: 'top', marginBottom: 15 },
});