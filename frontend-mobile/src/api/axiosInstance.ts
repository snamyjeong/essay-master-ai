import axios from 'axios'; // axios 라이브러리를 임포트하여 HTTP 통신을 준비합니다.
import Constants from 'expo-constants'; // Expo 설정값(app.json)을 읽어오기 위해 임포트합니다.
import * as SecureStore from 'expo-secure-store'; // 디바이스 보안 저장소를 사용하여 JWT 토큰을 관리합니다.

// 백엔드 서버의 기본 주소를 설정합니다.
const API_BASE_URL = 
  Constants.expoConfig?.extra?.EXPO_PUBLIC_API_URL || 
  'http://136.111.211.8:8000';

// Axios 인스턴스를 생성하여 공통 설정을 적용합니다.
const axiosInstance = axios.create({
  baseURL: API_BASE_URL, // 모든 요청의 기반 주소입니다.
  timeout: 60000, // 파일 분석 및 LLM 연산을 고려하여 타임아웃을 60초로 설정합니다.
  headers: {
    'Content-Type': 'application/json', // 기본 데이터 포맷은 JSON입니다.
    'Accept': 'application/json', // 서버로부터 JSON 응답을 받겠다고 선언합니다.
  },
});

/**
 * [Axios 요청 인터셉터]
 * 서버로 신호를 보내기 직전에 가로채서 필요한 작업을 수행합니다.
 */
axiosInstance.interceptors.request.use(
  async (config) => { // 토큰 조회가 비동기이므로 async 함수로 정의합니다.
    try {
      // 1. SecureStore에서 'userToken'이라는 키로 저장된 JWT를 조회합니다.
      const token = await SecureStore.getItemAsync('userToken');
      
      if (token) {
        // 2. 토큰이 존재하면 HTTP 헤더의 Authorization 필드에 담습니다.
        // Bearer 표준 스키마를 준수하여 백엔드의 검증 로직과 맞춥니다.
        config.headers.Authorization = `Bearer ${token}`;
        console.log('🔑 [Auth] 요청에 JWT 토큰을 포함했습니다.');
      }
    } catch (error) {
      console.error('❌ [Auth] 토큰 로드 중 오류 발생:', error);
    }

    // URL의 슬래시 중복이나 누락을 방지하는 안전 장치입니다.
    const base = config.baseURL?.endsWith('/') ? config.baseURL.slice(0, -1) : config.baseURL;
    const path = config.url?.startsWith('/') ? config.url : `/${config.url}`;
    
    console.log(`🚀 [API Request] ${config.method?.toUpperCase()} ${base}${path}`);
    return config; // 가공된 설정(config)을 반환하여 요청을 진행시킵니다.
  },
  (error) => {
    // 요청 과정에서 에러가 발생하면 거절(reject) 처리합니다.
    return Promise.reject(error);
  }
);

export default axiosInstance; // 고도화된 인스턴스를 내보냅니다.