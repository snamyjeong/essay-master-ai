import React, { useState } from 'react';
import { View, Text, TextInput, ScrollView, StyleSheet, Alert, ActivityIndicator } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import SoftCard from '../components/SoftCard';
import CustomButton from '../components/CustomButton';
import { evaluateEssayAnswer } from '../api/client'; // API 클라이언트 import

export default function QuizScreen() {
  const navigation = useNavigation();
  const [keywordAnswer, setKeywordAnswer] = useState('');
  const [isKeywordCorrect, setIsKeywordCorrect] = useState<boolean | null>(null);
  const [essayAnswer, setEssayAnswer] = useState('');
  const [isEvaluating, setIsEvaluating] = useState(false); // 로딩 상태 추가

  const handleKeywordSubmit = () => {
    if (keywordAnswer.toLowerCase().includes('ai')) { // 간단한 정답 로직
      setIsKeywordCorrect(true);
    } else {
      setIsKeywordCorrect(false);
    }
  };

  const handleEvaluateEssay = async () => { 
    if (essayAnswer.trim() === '') {
      Alert.alert('알림', '서술형 답안을 작성해주세요.'); // 알림 메시지도 기획에 맞춰 수정
      return;
    }

    setIsEvaluating(true); // 로딩 시작

    try {
      // API 호출
      const result = await evaluateEssayAnswer(essayAnswer);
      if (result && result.evaluationResult) {
        navigation.navigate('EvaluationResult', { evaluationData: result.evaluationResult });
      } else {
        Alert.alert('오류', '평가 결과를 받아오는데 실패했습니다.');
      }
    } catch (error) {
      console.error('평가 중 오류 발생:', error);
      Alert.alert('오류', '평가 중 문제가 발생했습니다. 다시 시도해주세요.');
    } finally {
      setIsEvaluating(false); // 로딩 종료
    }
  };

  return (
    <ScrollView style={styles.container}>
      {/* 키워드 퀴즈 영역 */}
      <SoftCard style={styles.sectionCard}>
        <Text style={styles.sectionTitle}>💡 키워드 퀴즈</Text>
        <Text style={styles.questionText}>Q1. 본문의 핵심 키워드는 무엇인가요?</Text>
        <View style={styles.answerInputContainer}>
          <TextInput
            style={styles.keywordInput}
            placeholder="정답을 입력하세요..."
            value={keywordAnswer}
            onChangeText={setKeywordAnswer}
          />
          <CustomButton
            title="✔️ 채점"
            onPress={handleKeywordSubmit}
            style={styles.scoreButton}
            textStyle={styles.scoreButtonText}
          />
        </View>
        {isKeywordCorrect !== null && (
          <Text style={[styles.feedbackText, isKeywordCorrect ? styles.correctText : styles.incorrectText]}>
            {isKeywordCorrect ? '✅ 정답입니다!' : '❌ 다시 시도해보세요.'}
          </Text>
        )}
      </SoftCard>

      {/* 심화학습 영역 (기획 변경 적용) */}
      <SoftCard style={styles.sectionCard}>
        {/* 기존 '심화학습 논술' -> '서술형 심화학습' 으로 수정 */}
        <Text style={styles.sectionTitle}>🚀 서술형 심화학습</Text>
        {/* 기존 '심화 논술 문제' -> '심화 서술형 문제' 로 수정 */}
        <Text style={styles.essayQuestion}>💡 심화 서술형 문제: AI 기술 발전이 사회에 미치는 긍정적/부정적 영향을 서술하고, 이에 대한 개인의 견해를 논하시오.</Text>
        <Text style={styles.guidelineText}>{`
[채점 가이드라인]
- 논리적 일관성: 20점
- 내용의 깊이: 30점
- 창의적 사고: 30점
- 분량 및 형식: 20점`}</Text>
        {/* 기존 '논술 답안' -> '서술형 심화 학습 내용' 으로 수정 */}
        <TextInput
          style={styles.essayInput}
          placeholder="여기에 서술형 심화 학습 내용을 작성하세요..."
          multiline
          textAlignVertical="top"
          value={essayAnswer}
          onChangeText={setEssayAnswer}
          editable={!isEvaluating} // 로딩 중에는 편집 불가
        />
        <CustomButton
          title={isEvaluating ? "평가 중..." : "📊 서술형 답안 평가"}
          onPress={handleEvaluateEssay}
          style={styles.evaluateButton}
          disabled={isEvaluating} // 로딩 중에는 버튼 비활성화
        >
          {isEvaluating && <ActivityIndicator color="#fff" style={styles.activityIndicator} />}
        </CustomButton>
      </SoftCard>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F3F4F6',
    padding: 20,
  },
  sectionCard: {
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    marginBottom: 15,
    color: '#333',
  },
  questionText: {
    fontSize: 17,
    marginBottom: 10,
    color: '#444',
  },
  answerInputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  keywordInput: {
    flex: 1,
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    marginRight: 10,
    backgroundColor: '#fff',
  },
  scoreButton: {
    paddingHorizontal: 20,
    paddingVertical: 12,
    minWidth: 80,
  },
  scoreButtonText: {
    fontSize: 16,
  },
  feedbackText: {
    fontSize: 16,
    fontWeight: 'bold',
    marginTop: 5,
    textAlign: 'center',
  },
  correctText: {
    color: '#28a745', // Green
  },
  incorrectText: {
    color: '#dc3545', // Red
  },
  essayQuestion: {
    fontSize: 17,
    fontWeight: 'bold',
    marginBottom: 10,
    color: '#444',
  },
  guidelineText: {
    fontSize: 14,
    color: '#666',
    marginBottom: 15,
    lineHeight: 20,
  },
  essayInput: {
    minHeight: 200,
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 15,
    fontSize: 16,
    lineHeight: 24,
    backgroundColor: '#fff',
    marginBottom: 20,
    textAlignVertical: 'top',
  },
  evaluateButton: {
    marginTop: 10,
    flexDirection: 'row', 
    alignItems: 'center', 
    justifyContent: 'center', 
  },
  activityIndicator: {
    marginLeft: 10,
  },
});