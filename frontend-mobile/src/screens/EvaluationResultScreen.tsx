import React, { useState } from 'react';
import { View, Text, TextInput, Button, StyleSheet, Alert, ScrollView } from 'react-native';
import axios from 'axios';
import Config from 'react-native-config';

const API_BASE_URL = Config.API_BASE_URL || 'http://localhost:8000'; // .env 파일에서 API 기본 URL 가져오기

interface EvaluationResult {
  overall_score: number;
  feedback: string;
  score_breakdown: { [key: string]: string };
  improved_answer_example: string;
}

const EvaluationResultScreen: React.FC = () => {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [evaluationResult, setEvaluationResult] = useState<EvaluationResult | null>(null);

  const handleEvaluateEssay = async () => {
    try {
      const token = 'YOUR_AUTH_TOKEN'; // 실제 인증 토큰으로 대체 필요

      const response = await axios.post(
        `${API_BASE_URL}/api/v1/learning/evaluate-essay`,
        { question, answer },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );
      setEvaluationResult(response.data); // 서버 응답을 상태에 저장
      Alert.alert('성공', '논술 평가가 완료되었습니다.');
    } catch (error) {
      console.error('논술 평가 실패:', error);
      Alert.alert('오류', '논술 평가 중 오류가 발생했습니다.');
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>논술 평가</Text>
      
      <Text style={styles.label}>문제:</Text>
      <TextInput
        style={styles.textArea}
        multiline
        numberOfLines={5}
        value={question}
        onChangeText={setQuestion}
        placeholder="AI가 출제한 논술 문제를 입력하세요..."
      />
      
      <Text style={styles.label}>답안:</Text>
      <TextInput
        style={styles.textArea}
        multiline
        numberOfLines={10}
        value={answer}
        onChangeText={setAnswer}
        placeholder="여기에 사용자의 논술 답안을 입력하세요..."
      />
      
      <Button title="논술 평가하기" onPress={handleEvaluateEssay} />

      {evaluationResult && (
        <View style={styles.resultContainer}>
          <Text style={styles.resultTitle}>평가 결과</Text>
          <Text style={styles.resultText}><Text style={{ fontWeight: 'bold' }}>종합 점수:</Text> {evaluationResult.overall_score}점</Text>
          <Text style={styles.resultText}><Text style={{ fontWeight: 'bold' }}>피드백:</Text> {evaluationResult.feedback}</Text>
          
          <Text style={styles.sectionTitle}>점수 상세:</Text>
          {Object.entries(evaluationResult.score_breakdown).map(([key, value]) => (
            <Text key={key} style={styles.itemText}><Text style={{ fontWeight: 'bold' }}>{key}:</Text> {value}</Text>
          ))}

          {evaluationResult.improved_answer_example && (
            <View>
              <Text style={styles.sectionTitle}>모범 답안 예시:</Text>
              <Text style={styles.itemText}>{evaluationResult.improved_answer_example}</Text>
            </View>
          )}
        </View>
      )}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#f5f5f5',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
    textAlign: 'center',
    color: '#333',
  },
  label: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 10,
    color: '#555',
  },
  textArea: {
    height: 100,
    borderColor: '#ddd',
    borderWidth: 1,
    borderRadius: 8,
    padding: 15,
    marginBottom: 20,
    backgroundColor: '#fff',
    fontSize: 16,
    lineHeight: 24,
    textAlignVertical: 'top',
  },
  resultContainer: {
    marginTop: 30,
    padding: 20,
    backgroundColor: '#e9f7ef',
    borderRadius: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  resultTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 15,
    color: '#28a745',
  },
  resultText: {
    fontSize: 16,
    marginBottom: 8,
    color: '#333',
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginTop: 15,
    marginBottom: 10,
    color: '#007bff',
  },
  itemText: {
    fontSize: 16,
    marginBottom: 5,
    color: '#333',
  },
});

export default EvaluationResultScreen;
