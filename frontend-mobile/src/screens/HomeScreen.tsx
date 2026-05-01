import React, { useState } from 'react';
import { View, Text, TextInput, Button, StyleSheet, Alert, ScrollView } from 'react-native';
import axios from 'axios';
import Config from 'react-native-config';

const API_BASE_URL = Config.API_BASE_URL || 'http://localhost:8000'; // .env 파일에서 API 기본 URL 가져오기

const HomeScreen: React.FC = () => {
  const [learningText, setLearningText] = useState('');
  const [generatedContent, setGeneratedContent] = useState<any>(null); // 생성된 콘텐츠 상태

  const handleGenerateContent = async () => {
    try {
      const token = 'YOUR_AUTH_TOKEN'; // 실제 인증 토큰으로 대체 필요

      const response = await axios.post(
        `${API_BASE_URL}/api/v1/learning/generate-content`,
        { text: learningText },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );
      setGeneratedContent(response.data); // 서버 응답을 상태에 저장
      Alert.alert('성공', '학습 콘텐츠가 성공적으로 생성되었습니다.');
    } catch (error) {
      console.error('학습 콘텐츠 생성 실패:', error);
      Alert.alert('오류', '학습 콘텐츠 생성 중 오류가 발생했습니다.');
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>학습 본문 입력</Text>
      <TextInput
        style={styles.textArea}
        multiline
        numberOfLines={10}
        value={learningText}
        onChangeText={setLearningText}
        placeholder="여기에 학습할 내용을 입력하세요..."
      />
      <Button title="학습 콘텐츠 생성" onPress={handleGenerateContent} />

      {generatedContent && (
        <View style={styles.contentContainer}>
          <Text style={styles.contentTitle}>생성된 학습 콘텐츠</Text>
          {generatedContent.quizzes && generatedContent.quizzes.length > 0 && (
            <View>
              <Text style={styles.sectionTitle}>퀴즈:</Text>
              {generatedContent.quizzes.map((quiz: any, index: number) => (
                <View key={index} style={styles.itemContainer}>
                  <Text style={styles.itemText}>- {quiz.question}</Text>
                  {quiz.options && quiz.options.map((option: string, optIndex: number) => (
                    <Text key={optIndex} style={styles.optionText}>  {String.fromCharCode(65 + optIndex)}. {option}</Text>
                  ))}
                  <Text style={styles.answerText}>정답: {quiz.answer}</Text>
                </View>
              ))}
            </View>
          )}
          {generatedContent.essay_question && (
            <View>
              <Text style={styles.sectionTitle}>논술 문제:</Text>
              <Text style={styles.itemText}>{generatedContent.essay_question}</Text>
            </View>
          )}
          {generatedContent.typing_practice && (
            <View>
              <Text style={styles.sectionTitle}>타자 연습:</Text>
              <Text style={styles.itemText}>{generatedContent.typing_practice}</Text>
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
  textArea: {
    height: 200,
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
  contentContainer: {
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
  contentTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 15,
    color: '#28a745',
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginTop: 15,
    marginBottom: 10,
    color: '#007bff',
  },
  itemContainer: {
    marginBottom: 10,
    padding: 10,
    backgroundColor: '#f0f8ff',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#add8e6',
  },
  itemText: {
    fontSize: 16,
    marginBottom: 5,
    color: '#333',
  },
  optionText: {
    fontSize: 14,
    marginLeft: 10,
    color: '#555',
  },
  answerText: {
    fontSize: 15,
    fontWeight: 'bold',
    color: '#dc3545',
    marginTop: 5,
  },
});

export default HomeScreen;
