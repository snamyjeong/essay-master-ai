import React, { useState, useEffect } from 'react'; // React 및 생명주기 훅 임포트
import { StatusBar } from 'expo-status-bar'; // 상태바 스타일링
import { StyleSheet, View, Button, ActivityIndicator } from 'react-native'; // 기본 컴포넌트 임포트
import * as SecureStore from 'expo-secure-store'; // 보안 저장소 임포트

// 화면 컴포넌트 임포트
import LoginScreen from './src/screens/LoginScreen'; // 로그인 화면
import UploadPdfScreen from './src/screens/UploadPdfScreen'; // PDF 업로드 화면
import QuizListScreen from './src/screens/QuizListScreen'; // 퀴즈 리스트 화면

export default function App() {
  const [isLoggedIn, setIsLoggedIn] = useState<boolean | null>(null); // 사용자의 로그인 인증 상태 관리
  const [currentScreen, setCurrentScreen] = useState<'upload' | 'quizList'>('upload'); // 현재 활성화된 서비스 화면

  // 1. [생명주기] 앱 초기 구동 시 저장된 토큰이 있는지 확인하여 자동 로그인 처리
  useEffect(() => {
    const checkLoginStatus = async () => {
      const token = await SecureStore.getItemAsync('userToken'); // 저장된 토큰 조회
      setIsLoggedIn(!!token); // 토큰이 존재하면 true, 없으면 false로 설정
    };
    checkLoginStatus();
  }, []);

  // 로그아웃 처리 함수
  const handleLogout = async () => {
    await SecureStore.deleteItemAsync('userToken'); // 보안 저장소에서 토큰 제거
    setIsLoggedIn(false); // 상태 업데이트하여 로그인 화면으로 전환
  };

  // 2. [조건부 렌더링] 토큰 확인 중일 때는 로딩 스피너 표시
  if (isLoggedIn === null) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color="#007AFF" />
      </View>
    );
  }

  // 3. [조건부 렌더링] 로그인이 안 되어 있으면 LoginScreen 표시
  if (!isLoggedIn) {
    return <LoginScreen onLoginSuccess={() => setIsLoggedIn(true)} />;
  }

  // 4. [조건부 렌더링] 로그인이 완료되었을 때의 실제 서비스 화면
  return (
    <View style={styles.container}>
      <StatusBar style="auto" />

      {/* 상단 내비게이션 바 역할 */}
      <View style={styles.buttonContainer}>
        <Button 
          title="PDF 업로드" 
          onPress={() => setCurrentScreen('upload')} 
          disabled={currentScreen === 'upload'} 
        />
        <Button 
          title="퀴즈 목록" 
          onPress={() => setCurrentScreen('quizList')} 
          disabled={currentScreen === 'quizList'} 
        />
        <Button title="로그아웃" onPress={handleLogout} color="red" />
      </View>

      {/* 현재 선택된 화면 렌더링 */}
      {currentScreen === 'upload' ? (
        <UploadPdfScreen onUploadSuccess={() => setCurrentScreen('quizList')} />
      ) : (
        <QuizListScreen />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff', paddingTop: 50 },
  centered: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  buttonContainer: { 
    flexDirection: 'row', 
    justifyContent: 'space-around', 
    padding: 10, 
    borderBottomWidth: 1, 
    borderColor: '#eee' 
  },
});