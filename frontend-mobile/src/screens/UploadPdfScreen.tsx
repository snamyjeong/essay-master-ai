import React, { useState } from 'react'; // React와 상태 관리 훅 임포트
import { View, Text, StyleSheet, Button, ActivityIndicator, Alert } from 'react-native'; // 기본 UI 컴포넌트 임포트
import * as DocumentPicker from 'expo-document-picker'; // 파일 선택을 위한 Expo 모듈
import axiosInstance from '../api/axiosInstance'; // 백엔드 통신용 Axios 인스턴스

// 컴포넌트 Props 타입 정의
interface UploadPdfScreenProps {
  onUploadSuccess: () => void; // 업로드 성공 시 호출될 콜백 함수
}

const UploadPdfScreen: React.FC<UploadPdfScreenProps> = ({ onUploadSuccess }) => {
  const [selectedFileName, setSelectedFileName] = useState<string | null>(null); // 파일명 저장 상태
  const [selectedFileUri, setSelectedFileUri] = useState<string | null>(null); // 파일 경로 저장 상태
  const [isLoading, setIsLoading] = useState<boolean>(false); // 로딩 애니메이션 상태

  // 파일 선택 핸들러
  const handleChoosePdf = async () => {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: 'application/pdf', // PDF 파일만 선택 가능하도록 제한
        copyToCacheDirectory: true, // 안드로이드 권한 문제를 피하기 위해 캐시로 복사
      });

      if (!result.canceled && result.assets && result.assets.length > 0) {
        setSelectedFileName(result.assets[0].name); // 선택된 파일 이름 저장
        setSelectedFileUri(result.assets[0].uri); // 선택된 파일 URI 저장
        console.log('Selected PDF URI:', result.assets[0].uri); // 디버깅용 로그 출력
      }
    } catch (err) {
      console.error('파일 선택 중 오류:', err);
      Alert.alert('오류', '파일을 선택하는 중 문제가 발생했습니다.');
    }
  };

  // 서버 업로드 핸들러
  const handleUploadPdf = async () => {
    if (!selectedFileUri) return;

    setIsLoading(true); // 로딩 시작
    try {
      const formData = new FormData(); // 멀티파트 폼 데이터 생성
      
      // React Native의 FormData 형식에 맞춰 객체 주입
      formData.append('file', {
        uri: selectedFileUri, // Expo에서 제공한 파일 URI
        name: selectedFileName || 'upload.pdf', // 파일명
        type: 'application/pdf', // 타입을 고정하여 mime 라이브러리 에러 방지
      } as any);

      // 백엔드 API 호출 (타임아웃 60초)
      const response = await axiosInstance.post('/api/v1/learning/upload-pdf', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      console.log('Upload Success:', response.data);
      Alert.alert('성공', 'PDF가 서버로 전송되었습니다.');
      onUploadSuccess(); // 성공 시 퀴즈 목록 화면으로 전환
    } catch (error: any) {
      console.error('Upload Error:', error.message);
      Alert.alert('업로드 실패', '백엔드 서버 연결 상태를 확인해주세요.');
    } finally {
      setIsLoading(false); // 로딩 종료
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Jarvis V3: PDF 분석</Text>
      <Button title="PDF 파일 선택" onPress={handleChoosePdf} disabled={isLoading} />
      {selectedFileName && (
        <View style={styles.infoBox}>
          <Text style={styles.fileName}>선택됨: {selectedFileName}</Text>
          <Button title="서버로 전송" onPress={handleUploadPdf} color="#28a745" />
        </View>
      )}
      {isLoading && <ActivityIndicator size="large" color="#007AFF" style={styles.loader} />}
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 20, backgroundColor: '#fff' },
  title: { fontSize: 24, fontWeight: 'bold', marginBottom: 30 },
  infoBox: { marginTop: 20, alignItems: 'center' },
  fileName: { marginBottom: 15, fontSize: 16, color: '#555' },
  loader: { marginTop: 20 },
});

export default UploadPdfScreen;