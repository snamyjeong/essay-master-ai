import React, { useState } from 'react'; // React와 상태 관리 훅 임포트
import { View, Text, TextInput, Button, StyleSheet, Alert, ActivityIndicator } from 'react-native'; // 기본 UI 컴포넌트 임포트
import * as SecureStore from 'expo-secure-store'; // 보안 저장소 임포트
import axiosInstance from '../api/axiosInstance'; // 설정된 Axios 인스턴스 임포트

// 로그인 성공 시 호출될 콜백 함수 타입 정의
interface LoginScreenProps {
  onLoginSuccess: () => void;
}

const LoginScreen: React.FC<LoginScreenProps> = ({ onLoginSuccess }) => {
  const [email, setEmail] = useState(''); // 이메일 입력 상태
  const [password, setPassword] = useState(''); // 비밀번호 입력 상태
  const [isLoading, setIsLoading] = useState(false); // 로딩 상태

  // 실제 로그인 처리 함수
  const handleLogin = async () => {
    // 필수 입력값 검증
    if (!email || !password) {
      Alert.alert('알림', '이메일과 비밀번호를 모두 입력해주세요.');
      return;
    }

    setIsLoading(true); // 로딩 애니메이션 시작
    try {
      // [핵심 수정] FastAPI의 OAuth2PasswordRequestForm 규격을 맞추기 위해 URLSearchParams를 사용합니다.
      const formData = new URLSearchParams();
      
      // 백엔드에서 이메일을 ID로 쓰더라도, 규격상 전송 키값은 반드시 'username'이어야 합니다.
      formData.append('username', email);
      
      // 사용자가 입력한 비밀번호를 추가합니다.
      formData.append('password', password);

      // 백엔드 인증 엔드포인트로 로그인 요청 전송
      // axiosInstance의 기본 JSON 설정을 덮어쓰기 위해 headers에 직접 Content-Type을 명시합니다.
      const response = await axiosInstance.post('/api/v1/auth/login', formData.toString(), {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

      // 서버로부터 응답받은 액세스 토큰 추출
      const { access_token } = response.data;

      // 토큰이 정상적으로 발급된 경우
      if (access_token) {
        // 토큰을 보안 저장소에 'userToken'이라는 키로 안전하게 저장
        // 이후 모든 요청에서 axiosInstance가 이 값을 꺼내 헤더에 자동으로 심어주게 됩니다.
        await SecureStore.setItemAsync('userToken', access_token);
        console.log('✅ [Auth] JWT 액세스 토큰 저장 완료');
        
        // 성공 콜백 호출하여 앱의 메인 화면(Dashboard)으로 네비게이션 전환
        onLoginSuccess();
      }
    } catch (error: any) {
      // 422 에러(규격 오류)나 401 에러(인증 실패) 발생 시 상세 로그 출력
      console.error('❌ [Login Error]', error.response?.data || error.message);
      // 사용자에게 친절한 에러 메시지 팝업 노출
      Alert.alert('로그인 실패', '아이디 또는 비밀번호를 확인해주세요.');
    } finally {
      setIsLoading(false); // 성공/실패 여부와 상관없이 로딩 상태 종료
    }
  };

  return (
    <View style={styles.container}>
      {/* 화면 제목 */}
      <Text style={styles.title}>Jarvis V3 로그인</Text>
      
      {/* 이메일 입력 필드 */}
      <TextInput
        style={styles.input}
        placeholder="이메일(ID)"
        value={email}
        onChangeText={setEmail}
        autoCapitalize="none" // 첫 글자 자동 대문자 방지
        keyboardType="email-address" // 이메일 입력에 최적화된 키보드 타입
      />
      
      {/* 비밀번호 입력 필드 */}
      <TextInput
        style={styles.input}
        placeholder="비밀번호"
        value={password}
        onChangeText={setPassword}
        secureTextEntry // 입력 내용 마스킹 처리
      />
      
      {/* 로그인 실행 버튼 - 로딩 중에는 클릭 비활성화 */}
      <Button 
        title={isLoading ? "로그인 중..." : "진행시켜"} 
        onPress={handleLogin} 
        disabled={isLoading} 
      />
      
      {/* 로딩 인디케이터 표시 */}
      {isLoading && <ActivityIndicator size="small" color="#0000ff" style={styles.loader} />}
    </View>
  );
};

// 화면 스타일 정의
const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', padding: 30, backgroundColor: '#fff' },
  title: { fontSize: 28, fontWeight: 'bold', marginBottom: 40, textAlign: 'center' },
  input: { borderWidth: 1, borderColor: '#ddd', padding: 15, marginBottom: 15, borderRadius: 8 },
  loader: { marginTop: 20 },
});

export default LoginScreen;