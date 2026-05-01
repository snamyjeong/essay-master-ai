import React, { useState, useRef, useEffect } from 'react';
import { 
  View, Text, TextInput, FlatList, TouchableOpacity, StyleSheet, 
  KeyboardAvoidingView, Platform, SafeAreaView, Image, Alert, Keyboard 
} from 'react-native';
import Ionicons from '@expo/vector-icons/Ionicons'; 
import * as ImagePicker from 'expo-image-picker'; 
import * as DocumentPicker from 'expo-document-picker'; 

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'ai';
  imageUri?: string;
  fileName?: string;
}

const ChatScreen: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    { id: '1', text: '안녕하세요 마스터님! 사진이나 파일을 올려주시면 분석해 드릴게요.', sender: 'ai' },
  ]);
  const [inputText, setInputText] = useState<string>('');
  const flatListRef = useRef<FlatList<Message>>(null);
  
  // 키보드 열림/닫힘 상태만 추적합니다.
  const [isKeyboardVisible, setKeyboardVisible] = useState(false);

  useEffect(() => {
    const showEvent = Platform.OS === 'ios' ? 'keyboardWillShow' : 'keyboardDidShow';
    const hideEvent = Platform.OS === 'ios' ? 'keyboardWillHide' : 'keyboardDidHide';

    const showSub = Keyboard.addListener(showEvent, () => setKeyboardVisible(true));
    const hideSub = Keyboard.addListener(hideEvent, () => setKeyboardVisible(false));
    
    return () => {
      showSub.remove();
      hideSub.remove();
    };
  }, []);

  useEffect(() => {
    flatListRef.current?.scrollToEnd({ animated: true });
  }, [messages]);

  // --- 멀티모달 로직 ---
  const takePhoto = async () => {
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    if (status !== 'granted') return Alert.alert('권한 알림', '카메라 권한이 필요합니다.');
    const result = await ImagePicker.launchCameraAsync({ allowsEditing: true, quality: 0.8 });
    if (!result.canceled) sendImageMessage(result.assets[0].uri);
  };

  const pickImage = async () => {
    const result = await ImagePicker.launchImageLibraryAsync({ mediaTypes: ImagePicker.MediaTypeOptions.Images, allowsEditing: true, quality: 0.8 });
    if (!result.canceled) sendImageMessage(result.assets[0].uri);
  };

  const pickDocument = async () => {
    try {
      const result = await DocumentPicker.getDocumentAsync({ type: "*/*" });
      if (!result.canceled) sendFileMessage(result.assets[0].name, result.assets[0].uri);
    } catch (err) { console.error("파일 오류:", err); }
  };

  const sendImageMessage = (uri: string) => {
    const newMessage: Message = { id: Date.now().toString(), text: '사진을 첨부했습니다.', sender: 'user', imageUri: uri };
    setMessages((prev) => [...prev, newMessage]);
    simulateAiResponse("이미지를 확인했습니다. 분석을 시작합니다.");
  };

  const sendFileMessage = (name: string, uri: string) => {
    const newMessage: Message = { id: Date.now().toString(), text: `파일 첨부: ${name}`, sender: 'user', fileName: name };
    setMessages((prev) => [...prev, newMessage]);
    simulateAiResponse(`${name} 파일을 분석하겠습니다.`);
  };

  const handleSendMessage = () => {
    if (inputText.trim() === '') return;
    const newMessage: Message = { id: Date.now().toString(), text: inputText, sender: 'user' };
    setMessages((prev) => [...prev, newMessage]);
    setInputText('');
    simulateAiResponse("최적의 답변을 준비 중입니다.");
  };

  const simulateAiResponse = (response: string) => {
    setTimeout(() => {
      const aiResponse: Message = { id: (Date.now() + 1).toString(), text: response, sender: 'ai' };
      setMessages((prev) => [...prev, aiResponse]);
    }, 1200);
  };

  const renderItem = ({ item }: { item: Message }) => {
    const isUser = item.sender === 'user';
    return (
      <View style={[styles.bubble, isUser ? styles.userBubble : styles.aiBubble]}>
        {item.imageUri && <Image source={{ uri: item.imageUri }} style={styles.attachedImage} />}
        {item.fileName && (
          <View style={styles.fileRow}>
            <Ionicons name="document-text" size={20} color={isUser ? "#fff" : "#1E90FF"} />
            <Text style={[styles.bubbleText, { marginLeft: 5 }]}>{item.fileName}</Text>
          </View>
        )}
        <Text style={isUser ? styles.userText : styles.aiText}>{item.text}</Text>
      </View>
    );
  };

  return (
    // [해결의 핵심 1] 가장 바깥쪽 껍데기에서 메뉴바 높이(115px)를 확보합니다.
    // 키보드가 열리면 여백을 10px로 줄여 하단으로 밀착시킵니다.
    <SafeAreaView style={[styles.safeArea, { paddingBottom: isKeyboardVisible ? 10 : 115 }]}>
      
      {/* 
        [해결의 핵심 2] 내부 뷰가 동적으로 변하지 않으므로 계산 오류가 없습니다.
        안드로이드도 padding을 주어 무조건 키보드 높이만큼 밀어 올리도록 강제합니다.
      */}
      <KeyboardAvoidingView 
        style={styles.container} 
        behavior={Platform.OS === 'ios' ? 'padding' : 'padding'} 
        keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}
      >
        <View style={styles.header}><Text style={styles.headerTitle}>메타 지식 AI 상담</Text></View>
        
        {/* 리스트와 입력창은 어떠한 꼼수 없이 자연스럽게 위치합니다. */}
        <FlatList
          ref={flatListRef}
          style={{ flex: 1 }}
          data={messages}
          renderItem={renderItem}
          keyExtractor={(item) => item.id}
          contentContainerStyle={{ padding: 15, paddingBottom: 20 }} 
        />

        <View style={{ paddingHorizontal: 15 }}>
          <View style={styles.floatingInputWrapper}>
            <View style={styles.toolBar}>
              <TouchableOpacity onPress={takePhoto} style={styles.toolButton}><Ionicons name="camera" size={24} color="#1E90FF" /></TouchableOpacity>
              <TouchableOpacity onPress={pickImage} style={styles.toolButton}><Ionicons name="image" size={24} color="#1E90FF" /></TouchableOpacity>
              <TouchableOpacity onPress={pickDocument} style={styles.toolButton}><Ionicons name="document-attach" size={24} color="#1E90FF" /></TouchableOpacity>
            </View>
            <View style={styles.inputRow}>
              <TextInput
                style={styles.textInput}
                value={inputText}
                onChangeText={setInputText}
                placeholder="메시지를 입력하세요..."
                onSubmitEditing={handleSendMessage}
              />
              <TouchableOpacity style={styles.sendButton} onPress={handleSendMessage}>
                <Ionicons name="send" size={20} color="#fff" />
              </TouchableOpacity>
            </View>
          </View>
        </View>
        
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: '#F3F4F6' },
  container: { flex: 1 },
  header: { padding: 15, backgroundColor: '#1E90FF', alignItems: 'center' },
  headerTitle: { color: '#fff', fontSize: 18, fontWeight: 'bold' },
  bubble: { maxWidth: '80%', padding: 12, borderRadius: 18, marginBottom: 12 },
  userBubble: { alignSelf: 'flex-end', backgroundColor: '#1E90FF', borderBottomRightRadius: 2 },
  aiBubble: { alignSelf: 'flex-start', backgroundColor: '#E5E7EB', borderBottomLeftRadius: 2 },
  userText: { color: '#fff', fontSize: 15 },
  aiText: { color: '#333', fontSize: 15 },
  bubbleText: { color: '#fff', fontSize: 14 },
  attachedImage: { width: 200, height: 150, borderRadius: 10, marginBottom: 8 },
  fileRow: { flexDirection: 'row', alignItems: 'center', marginBottom: 5 },
  floatingInputWrapper: {
    backgroundColor: '#fff',
    borderRadius: 25,
    padding: 10,
    elevation: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 5,
  },
  toolBar: { flexDirection: 'row', marginBottom: 5, paddingHorizontal: 10 },
  toolButton: { marginRight: 20 },
  inputRow: { flexDirection: 'row', alignItems: 'center' },
  textInput: { flex: 1, height: 40, paddingHorizontal: 15, backgroundColor: '#F9F9F9', borderRadius: 20, fontSize: 15 },
  sendButton: { backgroundColor: '#1E90FF', width: 40, height: 40, borderRadius: 20, justifyContent: 'center', alignItems: 'center', marginLeft: 10 },
});

export default ChatScreen;