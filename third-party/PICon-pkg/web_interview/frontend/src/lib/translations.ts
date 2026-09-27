/**
 * Translation data for English and Korean
 */

import { Language, ConsentStepContent } from '@/types/consent';

interface Translations {
  common: {
    next: string;
    previous: string;
    start: string;
    continue: string;
    language: string;
    name: string;
    enterName: string;
    loading: string;
    error: string;
  };
  home: {
    title: string;
    subtitle: string;
    description: string;
    privacyNote: string;
    nameLabel: string;
    namePlaceholder: string;
    continueButton: string;
    errorName: string;
    errorStart: string;
    existingSessionTitle: string;
    existingSessionDescription: string;
    continueSession: string;
    startNewInterview: string;
  };
  consent: {
    title: string;
    progressLabel: string;
    warning: string;
    steps: ConsentStepContent[];
    startInterview: string;
  };
  interview: {
    title: string;
    participantLabel: string;
    phases: {
      predefined: string;
      main: string;
      repeat: string;
      complete: string;
    };
    questionProgress: string;
    inputPlaceholder: string;
    sendButton: string;
    pressEnterHint: string;
    completeTitle: string;
    completeMessage: string;
  };
}

export const translations: Record<Language, Translations> = {
  en: {
    common: {
      next: 'Next',
      previous: 'Previous',
      start: 'Start Interview',
      continue: 'Continue',
      language: 'Language',
      name: 'Name',
      enterName: 'Enter your name',
      loading: 'Loading...',
      error: 'Error',
    },
    home: {
      title: 'Human Interview Study',
      subtitle: 'Welcome',
      description: 'Welcome! This interview will take approximately 1 hour. You will be asked around 70 questions about yourself. Please answer honestly - you may decline to answer any question that makes you uncomfortable.',
      privacyNote: '⚠️ Please do not use the back button, reload, or close this page during the interview.',
      nameLabel: 'Your Name',
      namePlaceholder: 'Enter your name',
      continueButton: 'Continue to Consent',
      errorName: 'Please enter your name',
      errorStart: 'Failed to start interview. Please try again.',
      existingSessionTitle: 'You have an ongoing interview',
      existingSessionDescription: 'Your previous session is saved. Would you like to continue where you left off, or start a new interview?',
      continueSession: 'Continue Interview',
      startNewInterview: 'Start New Interview',
    },
    consent: {
      title: 'Informed Consent',
      progressLabel: 'Step {current} of {total}',
      startInterview: 'Start Interview',
      warning: 'Before participating in this survey, please read and understand the consent form and instructions carefully. As this is a **paid study**, we kindly ask for your **sincere and thoughtful responses to all questions**. We appreciate your valuable time, and to ensure accurate data collection, **please note that compensation may be limited if insincere or false responses are identified.**',
      steps: [
        {
          title: 'Interview Nature & Resources',
          description: 'This interview is designed as a **stress test** where the interviewer may question or verify your responses. Think of it as proving your identity - you are demonstrating that you are who you say you are.',
          details: [
            'The interviewer may ask probing questions to verify your responses',
            'It is **always better to attempt an answer** rather than saying "I don\'t know" or evading the question',
            'If the interviewer asks about factual elements (e.g., building names, place names, dates), please **use Google or other search engines** to look up information and attempt to answer as best as you can',
            'If the interviewer directly provides the relevant URL links, **please visit the site, review the content, and use it to inform your answers**',
            'Taking time to research your answer is completely acceptable',
          ],
          checkboxLabel: 'I understand the interview nature and that attempting to answer is better than evasion',
        },
        {
          title: 'Commitment to Honesty',
          description: 'Please be truthful in all questions. If you do not want to provide further information, clearly express your refusal rather than providing false information.',
          details: [
            'Honest responses help us conduct meaningful research',
            'If you prefer not to answer, simply state your refusal clearly',
            'There is no penalty for declining to answer',
          ],
          checkboxLabel: 'I commit to answering truthfully or clearly stating my refusal',
        },
        {
          title: 'Technical Requirements',
          description: 'Please do NOT reload or exit the page during the interview.',
          details: [
            'Reloading the page will cause you to lose your interview progress',
            'You will need to start over from the beginning if you refresh',
            'Please keep this browser tab open until the interview is complete',
          ],
          checkboxLabel: 'I understand I should not reload or close this page during the interview',
        },
        {
          title: 'Interview Structure',
          description: 'This interview will take up to a maximum of 1 hour and consists of three phases:',
          details: [
            '1. 10 demographic questions to get to know you',
            '2. 40+ follow-up questions based on your responses',
            '3. Repeating some questions for clarification',
          ],
          checkboxLabel: 'I understand the interview structure and time commitment (~1 hour)',
        },
        {
          title: 'Your Rights and Privacy',
          description: 'If the questions are inappropriate or uncomfortable in any sense (e.g., invasion of privacy), you may refuse to provide the response.',
          details: [
            'You have the right to decline any question that makes you uncomfortable',
            'You can abstain from providing a response',
            'You can even change the topic by saying, for example, "can we talk about something else?"',
          ],
          checkboxLabel: 'I understand I can decline to answer any question that makes me uncomfortable',
        },
        {
          title: 'Data Usage and Protection',
          description: 'Collecting your information is solely for research purposes. We ensure that your information will be protected and NOT be used in any other way.',
          details: [
            'Your personal information will be kept confidential and secure',
            'Data will only be used for this research project',
            'Your information will be deleted as soon as the research project is over',
            'We will never share your data with third parties',
          ],
          checkboxLabel: 'I consent to my data being collected and used for research purposes only',
        },
      ],
    },
    interview: {
      title: 'Human Interview',
      participantLabel: 'Participant',
      phases: {
        predefined: 'Part 1: Getting to Know You',
        main: 'Part 2: Follow-up Questions',
        repeat: 'Part 3: Clarification',
        complete: 'Complete',
      },
      questionProgress: 'Question {current} of ~{total}',
      inputPlaceholder: 'Type your response...',
      sendButton: 'Send',
      pressEnterHint: 'Press Enter to send • You may decline to answer any question',
      completeTitle: 'Interview Complete! 🎉',
      completeMessage: 'Thank you for your participation. Please do not close this page until you see a confirmation message.',
    },
  },
  ko: {
    common: {
      next: '다음',
      previous: '이전',
      start: '인터뷰 시작',
      continue: '계속하기',
      language: '언어',
      name: '이름',
      enterName: '이름을 입력하세요',
      loading: '로딩 중...',
      error: '오류',
    },
    home: {
      title: '인간 인터뷰 연구',
      subtitle: '환영합니다',
      description: '환영합니다! 이 인터뷰는 약 1시간이 소요됩니다. 귀하에 대한 약 60-80개의 질문을 받게 됩니다. 정직하게 답변해 주세요. 불편한 질문은 답변을 거부할 수 있습니다.',
      privacyNote: '⚠️ 인터뷰 중에 페이지를 뒤로가기, 새로고침하거나 닫지 마세요.',
      nameLabel: '귀하의 이름',
      namePlaceholder: '이름을 입력하세요',
      continueButton: '동의서로 계속',
      errorName: '이름을 입력해 주세요',
      errorStart: '인터뷰 시작에 실패했습니다. 다시 시도해 주세요.',
      existingSessionTitle: '진행 중인 인터뷰가 있습니다',
      existingSessionDescription: '이전 세션이 저장되어 있습니다. 이어서 진행하시겠습니까, 아니면 새로운 인터뷰를 시작하시겠습니까?',
      continueSession: '인터뷰 이어하기',
      startNewInterview: '새 인터뷰 시작',
    },
    consent: {
      title: '사전 동의서',
      progressLabel: '{total}단계 중 {current}단계',
      startInterview: '인터뷰 시작',
      warning: '본 설문에 참여하시기 전, 동의서의 내용 및 주의사항을 충분히 숙지해 주시기 바랍니다. 본 조사는 유급으로 진행되는 만큼, **모든 문항에 대하여 참여자분의 진솔하고 성의 있는 답변을 부탁드립니다.** 귀한 시간 내어 주시는 만큼 정확한 자료 수집을 위해, **불성실하거나 허위의 응답이 확인될 경우 사례비 지급에 제한이 있을 수 있음을 양해 부탁드립니다.**',
      steps: [
        {
          title: '인터뷰 성격 및 리소스',
          description: '이 인터뷰는 심문관이 귀하에 대해 매우 집요하게 질문하는 **스트레스 테스트**로 설계되었습니다. 귀하의 신원을 증명하는 것처럼 생각하세요 - 귀하 본인이 맞다는 것을 입증하는 심문이라고 생각하시면 됩니다.',
          details: [
            '심문관은 귀하의 답변을 확인하기 위해 심층적인 질문을 할 수 있습니다.',
            '"모르겠습니다"라고 말하거나 질문을 회피하는 것보다 **답변을 시도하는 것이 항상 더 좋습니다**.',
            '사실적인 요소(건물명, 지명, 날짜 등)에 관한 질문의 경우, **Google 등의 검색 엔진을 사용하여** 최대한 답변을 시도해주세요.',
            '심문관이 직접 관련 URL 링크를 제공하는 경우, 사이트에 접속하여 내용을 확인한 후 답변에 활용해주세요.',
            '답변을 위해 관련된 정보를 탐색하는 데 충분히 시간을 가지셔도 됩니다.',
          ],
          checkboxLabel: '인터뷰 성격을 이해하며 회피보다 답변 시도가 더 낫다는 것을 이해했습니다',
        },
        {
          title: '정직성 약속',
          description: '모든 질문에 대해 진실하게 답변해 주세요. 추가 정보를 제공하고 싶지 않으시면 거짓 정보를 제공하는 대신 명확하게 거부 의사를 표현해 주세요.',
          details: [
            '정직한 답변은 의미 있는 연구를 수행하는 데 도움이 됩니다',
            '답변하고 싶지 않으시면 명확하게 거부 의사를 표현해 주세요',
            '답변 거부에 대한 불이익은 없습니다',
          ],
          checkboxLabel: '진실하게 답변하거나 명확하게 거부 의사를 표현하겠습니다',
        },
        {
          title: '⚠️ 기술적 요구사항 (필독)',
          description: '인터뷰 데이터 유실을 방지하기 위해 아래 내용을 반드시 지켜주세요.',
          details: [
            '**새로고침 금지**: 페이지를 새로고침하거나 창을 닫으면 진행 상황이 모두 사라져 처음부터 다시 시작해야 합니다.',
            '**정보 검색 팁**: 정보 검색을 하실 때는 새 탭이나 스마트폰을 별도로 이용해 주세요.',
            '**응답 타임아웃**: 장시간 동안 (1시간 이상) 응답이 없으면 서버 연결이 끊어집니다. 원활한 진행을 위해 1시간 정도를 비우시고 인터뷰를 한 번에 완료하시는 것을 추천 드립니다.',
          ],
          checkboxLabel: '인터뷰 중 새로고침, 새로운 탭 이용, 응답 타임아웃과 관련된 주의사항을 이해했습니다',
        },
        {
          title: '인터뷰 구조',
          description: '이 인터뷰는 최대 1시간이 소요되며 3단계로 진행됩니다:',
          details: [
            '1. 귀하를 알아가기 위한 10개의 인구통계학적 질문',
            '2. 귀하의 답변을 기반으로 한 40개 이상의 후속 질문',
            '3. 명확화를 위한 일부 질문 반복',
          ],
          checkboxLabel: '인터뷰 구조와 시간 소요(약 1시간)를 이해했습니다',
        },
        {
          title: '귀하의 권리 및 개인정보 보호',
          description: '부적절하거나 불편한 질문(예: 사생활 침해)이 있을 경우 답변을 거부할 수 있습니다.',
          details: [
            '불편한 질문에 대해서는 답변을 거부할 권리가 있습니다',
            '답변 제공을 거부할 수 있습니다',
            '예를 들어 "다른 주제에 대해 이야기할 수 있을까요?"라고 말하여 주제를 변경할 수도 있습니다',
          ],
          checkboxLabel: '불편한 질문에 대해서는 답변을 거부할 수 있음을 이해했습니다',
        },
        {
          title: '데이터 사용 및 보호',
          description: '귀하의 정보 수집은 연구 목적으로만 이루어집니다. 귀하의 정보는 보호되며 다른 방식으로 사용되지 않을 것을 보장합니다.',
          details: [
            '귀하의 개인 정보는 기밀로 유지되고 안전하게 보호됩니다',
            '데이터는 이 연구 프로젝트에만 사용됩니다',
            '연구 프로젝트가 종료되는 즉시 귀하의 정보는 삭제됩니다',
            '귀하의 데이터를 제3자와 공유하지 않습니다',
          ],
          checkboxLabel: '연구 목적으로만 데이터를 수집하고 사용하는 것에 동의합니다',
        },
      ],
    },
    interview: {
      title: '인간 인터뷰',
      participantLabel: '참여자',
      phases: {
        predefined: '1부: 귀하 알아가기',
        main: '2부: 후속 질문',
        repeat: '3부: 명확화',
        complete: '완료',
      },
      questionProgress: '약 {total}개 중 {current}번째 질문',
      inputPlaceholder: '답변을 입력하세요...',
      sendButton: '전송',
      pressEnterHint: 'Enter를 눌러 전송 • 모든 질문에 대해 답변을 거부할 수 있습니다',
      completeTitle: '인터뷰 완료! 🎉',
      completeMessage: '참여해 주셔서 감사합니다. 확인 메시지가 표시될 때까지 이 페이지를 닫지 마세요.',
    },
  },
};

export function getTranslation(language: Language): Translations {
  return translations[language];
}
