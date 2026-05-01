import React, { useState } from 'react'; // React와 상태 관리 훅 임포트
import { View, Text, TextInput, StyleSheet, ActivityIndicator, TouchableOpacity, Alert } from 'react-native'; // 기본 UI 컴포넌트 임포트
import * as SecureStore from 'expo-secure-store'; // 보안 저장소 임포트
import axiosInstance from '../api/axiosInstance'; // 설정된 Axios 인스턴스 임포트
import SoftCard from '../components/SoftCard'; // UI 통일성을 위한 컴포넌트 임포트
import CustomButton from '../components/CustomButton'; // UI 통일성을 위한 컴포넌트 임포트

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
      {/* 화면 제목 (기획 변경 반영) */}
      <Text style={styles.title}>📖 학습 마스터 AI </Text>
      
      {/* 폼 전체를 SoftCard로 감싸서 다른 화면과 UI 일관성 유지 */}
      <SoftCard style={styles.card}>
        {/* 이메일 입력 필드 */}
        <TextInput
          style={styles.input}
          placeholder="이메일(ID)"
          value={email}
          onChangeText={setEmail}
          autoCapitalize="none" // 첫 글자 자동 대문자 방지
          keyboardType="email-address" // 이메일 입력에 최적화된 키보드 타입
          placeholderTextColor="#999" // 플레이스홀더 색상 지정
        />
        
        {/* 비밀번호 입력 필드 */}
        <TextInput
          style={styles.input}
          placeholder="비밀번호"
          value={password}
          onChangeText={setPassword}
          secureTextEntry // 입력 내용 마스킹 처리
          placeholderTextColor="#999"
        />
        
        {/* 로그인 실행 버튼 - 시그니처 문구 유지 및 CustomButton 적용 */}
        <CustomButton 
          title={isLoading ? "로그인 중..." : "진행시켜"} 
          onPress={handleLogin} 
          disabled={isLoading} 
          style={styles.loginButton}
        />
        {/* 추가: 계정 지원 메뉴 (회원가입 / 아이디 찾기 / 비밀번호 찾기) */}
        <View style={styles.helperContainer}>
          <TouchableOpacity onPress={() => Alert.alert('안내', '회원가입 화면으로 이동합니다. (준비 중)')}>
            <Text style={styles.helperText}>회원가입</Text>
          </TouchableOpacity>
          
          <Text style={styles.divider}>|</Text>
          
          <TouchableOpacity onPress={() => Alert.alert('안내', '아이디 찾기 화면으로 이동합니다. (준비 중)')}>
            <Text style={styles.helperText}>아이디 찾기</Text>
          </TouchableOpacity>
          
          <Text style={styles.divider}>|</Text>
          
          <TouchableOpacity onPress={() => Alert.alert('안내', '비밀번호 찾기 화면으로 이동합니다. (준비 중)')}>
            <Text style={styles.helperText}>비밀번호 찾기</Text>
          </TouchableOpacity>
        </View>
        
        {/* 로딩 인디케이터 표시 */}
        {isLoading && <ActivityIndicator size="small" color="#fff" style={styles.loader} />}
      </SoftCard>
    </View>
  );
};

// 화면 스타일 정의
const styles = StyleSheet.create({
  // 앱 전체 공통 배경색(#F3F4F6)으로 변경하여 통일감 부여
  container: { flex: 1, justifyContent: 'center', padding: 20, backgroundColor: '#F3F4F6' },
  title: { fontSize: 28, fontWeight: 'bold', marginBottom: 40, textAlign: 'center', color: '#333' },
  card: { padding: 25 }, // 내부 컴포넌트 여백
  input: { 
    borderWidth: 1, 
    borderColor: '#E0E0E0', 
    padding: 15, 
    marginBottom: 15, 
    borderRadius: 10, 
    backgroundColor: '#fff',
    fontSize: 16 
  },
  loginButton: { marginTop: 10 },
  loader: { position: 'absolute', bottom: 35, alignSelf: 'center' }, // 로딩 스피너 위치 조정
  // 계정 지원 메뉴(회원가입 등)를 가로로 나란히 중앙 정렬하는 컨테이너 스타일입니다.
  helperContainer: {
    flexDirection: 'row', // 가로 배치
    justifyContent: 'center', // 중앙 정렬
    alignItems: 'center', // 세로 높이 맞춤
    marginTop: 25, // 로그인 버튼과 간격 띄우기
  },
  // 계정 지원 메뉴의 텍스트 스타일입니다. (차분한 회색조 적용)
  helperText: {
    fontSize: 14,
    color: '#64748B',
    fontWeight: '500',
  },
  // 계정 지원 메뉴 사이의 구분선(|) 스타일입니다.
  divider: {
    fontSize: 12,
    color: '#CBD5E1', // 연한 회색
    marginHorizontal: 12, // 좌우 여백 주어 텍스트와 분리
  },  
});

export default LoginScreen;