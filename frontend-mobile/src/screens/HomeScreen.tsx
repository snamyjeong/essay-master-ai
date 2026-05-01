import React, { useState } from 'react';
import { View, Text, TextInput, ScrollView, StyleSheet, Alert, ActivityIndicator, TouchableOpacity } from 'react-native'; // TouchableOpacity 추가
import { useNavigation } from '@react-navigation/native';
import SoftCard from '../components/SoftCard';
import CustomButton from '../components/CustomButton';
import { generateLearningContent } from '../api/client';
import * as DocumentPicker from 'expo-document-picker'; // 기기 내부 파일 선택기
import * as FileSystem from 'expo-file-system';       // 물리적 파일 시스템 읽기/쓰기 도구
import { Ionicons } from '@expo/vector-icons';

export default function HomeScreen() {
  const navigation = useNavigation();
  // 기획 변경 반영: 변수명을 essayText에서 learningText로 수정하여 혼선 방지
  const [learningText, setLearningText] = useState(''); 
  const [isLoading, setIsLoading] = useState(false); // API 호출 시 로딩 스피너 제어

  // [파일 업로드 로직] txt 파일의 텍스트를 파싱하여 입력창에 넣어줍니다.
  const handleFileUpload = async () => {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: ["text/plain", "application/pdf"], 
        copyToCacheDirectory: true, 
      });

      console.log("File selection result:", result);

      if (result.canceled) {
        console.log("File selection cancelled.");
        return; 
      }

      // [422 에러 대비 견고한 처리] 자산(assets) 배열이 정상적으로 존재하는지 검증
      if (!result.assets || result.assets.length === 0) {
        Alert.alert('오류', '파일을 정상적으로 가져오지 못했습니다.');
        return;
      }

      const asset = result.assets[0];
      const uri = asset.uri;
      // name이 없는 특이 케이스를 대비해 uri에서 직접 파일명을 강제 추출하는 방어 코드 추가
      const name = asset.name || uri.split('/').pop() || 'unknown.txt'; 

      const fileExtension = name.split('.').pop()?.toLowerCase();

      // 확장자 체크 강화 (.txt, .text 모두 허용)
      if (fileExtension === 'txt' || fileExtension === 'text') {
        const fileContent = await FileSystem.readAsStringAsync(uri);
        console.log("읽은 텍스트 내용 (디버깅):", fileContent); // 데이터 누락 확인용
        setLearningText(fileContent); // 읽어온 내용을 UI 상태에 주입
        Alert.alert('성공', `${name} 파일이 업로드되었습니다.`);
      } 
      else if (fileExtension === 'pdf') {
        Alert.alert('알림', 'PDF 파일의 텍스트 추출은 백엔드 연동이 필요합니다. 곧 업데이트 예정입니다.', [{ text: '확인' }]);
        setLearningText(`[PDF] ${name}`); // PDF는 임시로 이름만 표시
      } 
      else {
        Alert.alert('오류', '지원하지 않는 파일 형식입니다. .txt 또는 .pdf 파일을 선택해주세요.', [{ text: '확인' }]);
      }
    } catch (error) {
      console.error('Error picking document:', error); 
      Alert.alert('오류', '파일 업로드 중 오류가 발생했습니다. 다시 시도해주세요.', [{ text: '확인' }]); 
    }
  };

  // [AI 분석 통신 로직] 입력된 텍스트를 백엔드로 보내 문제를 생성합니다.
  const handleAnalyzeAndGenerate = async () => {
    if (learningText.trim() === '') {
      Alert.alert('알림', '내용을 입력해주세요.');
      return;
    }

    setIsLoading(true); 
    try {
      // client.ts의 generateLearningContent 함수를 호출 (백엔드와 통신)
      const result = await generateLearningContent(learningText);
      console.log('API Response:', result); 
      Alert.alert('성공', result.message || '학습 콘텐츠 생성이 완료되었습니다.'); 
      navigation.navigate('QuizStack'); // 성공 시 퀴즈 화면으로 전환
    } catch (error) {
      console.error('Failed to generate learning content:', error); 
      // 422 에러 발생 시 사용자에게 명확한 가이드라인 알림
      Alert.alert('오류', '학습 콘텐츠 생성에 실패했습니다. (데이터 형식을 확인해주세요.)'); 
    } finally {
      setIsLoading(false); 
    }
  };

  return (
    <ScrollView style={styles.container}>
      {/* 최상단 타이틀 영역 좌측에 대시보드로 돌아갈 수 있는 🏠 홈 버튼 추가 */}
      <View style={styles.headerContainer}>
        {/* UI 변경: 에세이 마스터 AI -> 암기 학습 마스터 AI */}
        <Text style={styles.title}>📝 암기 학습 마스터 AI</Text>
      </View>

      <SoftCard style={styles.inputCard}>
        <TextInput
          style={styles.textInput}
          /* UI 변경: placeholder 텍스트 수정 */
          placeholder="여기에 학습 내용을 입력하세요..."
          multiline
          textAlignVertical="top"
          value={learningText} // 변경된 상태 변수 연결
          onChangeText={setLearningText} 
        />
      </SoftCard>

      <View style={styles.buttonContainer}>
        <CustomButton
          title="📂 파일 업로드"
          onPress={handleFileUpload} 
          style={styles.button}
        />
        <CustomButton
          title={isLoading ? "🧠 분석 중..." : "🧠 AI 분석 및 문제 생성"} 
          onPress={handleAnalyzeAndGenerate} 
          style={styles.button}
          disabled={isLoading} 
        >
          {isLoading && <ActivityIndicator color="#fff" style={{ marginLeft: 10 }} />} 
        </CustomButton>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F3F4F6',
    padding: 20,
  },
  headerContainer: { // 홈 버튼과 타이틀을 위한 컨테이너 추가
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center', // 타이틀을 중앙으로 이동
    marginBottom: 25,
    position: 'relative', // 홈 버튼 위치 조정을 위해
  },
  homeButton: {
    position: 'absolute',
    left: 0,
    padding: 5, // 터치 영역 확보
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    // marginBottom: 25, // headerContainer로 이동
    color: '#333',
    flex: 1, // 타이틀이 가능한 공간을 모두 차지하여 중앙 정렬에 도움
    textAlign: 'center', // 텍스트 자체를 중앙 정렬
  },
  inputCard: {
    marginBottom: 20,
  },
  textInput: {
    minHeight: 200,
    fontSize: 16,
    lineHeight: 24,
    padding: 15,
    color: '#333',
  },
  buttonContainer: {
    flexDirection: 'column',
    justifyContent: 'center',
    alignItems: 'center',
  },
  button: {
    width: '100%',
    marginBottom: 15,
  },
});