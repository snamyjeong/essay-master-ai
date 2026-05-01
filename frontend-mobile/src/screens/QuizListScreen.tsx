import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import SoftCard from '../components/SoftCard';
import CustomButton from '../components/CustomButton';

const QuizListScreen = () => {
  return (
    // [수정] scrollContent 하단 여백을 40 -> 110으로 상향 조정
    <ScrollView style={styles.container} contentContainerStyle={styles.scrollContent}>
      <Text style={styles.title}>🦉 학습 퀴즈 리스트</Text>
      <SoftCard style={styles.card}>
        <Text style={styles.emptyTitle}>아직 생성된 퀴즈가 없습니다.</Text>
        <Text style={styles.emptySub}>문서를 업로드하고 AI 분석을 통해 퀴즈를 만들어보세요.</Text>
      </SoftCard>
      <SoftCard style={styles.card}>
        <Text style={styles.quizTitle}>📌 [예시] AI 기술 발전과 사회적 영향</Text>
        <Text style={styles.quizInfo}>총 3문제 • 서술형 및 키워드 포함</Text>
        <CustomButton title="🚀 퀴즈 풀기" onPress={() => console.log('퀴즈 시작')} style={styles.startButton} />
      </SoftCard>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F3F4F6' },
  scrollContent: { padding: 20, paddingBottom: 110 }, // 플로팅 메뉴 가림 방지
  title: { fontSize: 26, fontWeight: 'bold', marginBottom: 20, textAlign: 'center', color: '#333' },
  card: { marginBottom: 15, padding: 20 },
  emptyTitle: { fontSize: 18, fontWeight: 'bold', color: '#555', textAlign: 'center', marginBottom: 10 },
  emptySub: { fontSize: 14, color: '#777', textAlign: 'center', lineHeight: 22 },
  quizTitle: { fontSize: 18, fontWeight: 'bold', color: '#333', marginBottom: 8 },
  quizInfo: { fontSize: 14, color: '#666', marginBottom: 15 },
  startButton: { marginTop: 5 },
});

export default QuizListScreen;