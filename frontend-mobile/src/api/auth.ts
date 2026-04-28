// frontend-mobile/src/api/auth.ts

// 수석님이 완벽하게 작성해두신 공통 Axios 인스턴스를 가져옵니다.
import axiosInstance from './axiosInstance'; 
// 로그인 성공 시 발급받은 JWT 토큰을 안전하게 저장하기 위해 SecureStore를 임포트합니다.
import * as SecureStore from 'expo-secure-store'; 

// 이메일과 비밀번호를 인자로 받아 백엔드에 로그인을 요청하는 비동기 함수입니다.
export const loginAPI = async (email: string, password: string) => {
  try {
    // FastAPI의 OAuth2PasswordRequestForm 규격인 Form-Data 형식을 맞추기 위해 URLSearchParams 객체를 생성합니다.
    const formData = new URLSearchParams();

    // 백엔드 로그인 로직이 이메일을 기반으로 하더라도, FastAPI 표준 규격상 전송하는 키 이름은 반드시 'username'이어야 합니다.
    formData.append('username', email);

    // 사용자가 입력한 평문 비밀번호를 폼 데이터에 추가합니다.
    formData.append('password', password);

    // 공통 인스턴스를 사용하여 백엔드의 로그인 엔드포인트로 POST 요청을 보냅니다.
    const response = await axiosInstance.post(
      '/api/v1/auth/login', // 요청을 보낼 목적지 주소 (baseURL 뒤에 붙음)
      formData.toString(),  // URLSearchParams 객체를 URL 인코딩된 문자열(x-www-form-urlencoded)로 변환하여 본문에 담습니다.
      {
        headers: {
          // axiosInstance.ts에 설정된 전역 'application/json' 헤더를 무시하고, 이 요청에만 Form-Data 형식을 강제 적용합니다.
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      }
    );

    // 서버 응답 객체에서 JWT 액세스 토큰을 추출합니다.
    const token = response.data.access_token;

    // 추출한 토큰이 정상적으로 존재한다면 디바이스의 암호화된 저장소에 보관합니다.
    if (token) {
      // 'userToken'이라는 키값으로 저장하면, 이후 axiosInstance의 인터셉터가 이 값을 꺼내서 모든 API 요청 헤더에 자동으로 심어줍니다.
      await SecureStore.setItemAsync('userToken', token);
      console.log('✅ [Login] JWT 토큰 SecureStore 저장 완료');
    }

    // 화면(UI) 컴포넌트에서 후처리(예: 메인 화면으로 라우팅)를 할 수 있도록 응답 데이터를 그대로 반환합니다.
    return response.data;

  } catch (error) {
    // 네트워크 오류, 401 인증 실패, 422 규격 오류 등이 발생하면 콘솔에 로그를 남깁니다.
    console.error('❌ [Auth API] 로그인 요청 실패:', error);
    // 에러를 상위(호출한 컴포넌트)로 던져서 화면에 경고창(Alert) 등을 띄울 수 있도록 합니다.
    throw error;
  }
};