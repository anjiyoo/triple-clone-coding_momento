document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('userInput');
    
    // 데이터 값을 HTML 데이터 속성에서 가져오기
    const planResultElement = document.getElementById('planResult');
    const who = planResultElement.getAttribute('data-who');
    const date = planResultElement.getAttribute('data-date');
    const city = planResultElement.getAttribute('data-city');
    const autoQuery = `${who} 떠나는 ${date}, ${city} 여행컨셉을 추천해줘`;

    // 자동 질문을 GPT에 보냄
    function sendQuery(query) {
        if (!query.trim()) {
            console.log(query)
            // 입력 필드가 비어있을 경우 메시지 표시
            const recommendquestionDiv = document.createElement('div');
            recommendquestionDiv.className = 'recommend';
            chatMessages.appendChild(recommendquestionDiv);
            return; // 함수 실행 중지
        }
        console.log(query)

        // 채팅창에 사용자 입력 바로 표시
        const questionDiv = document.createElement('div');
        questionDiv.textContent = query;
        questionDiv.className = 'question';  // 질문에 'question' 클래스 추가
        chatMessages.appendChild(questionDiv);

        // 서버 응답을 기다리는 동안의 메시지
        const waitingDiv = document.createElement('div');
        waitingDiv.textContent = "...";
        waitingDiv.className = 'waiting';  // 대기 메시지에 'waiting' 클래스 추가
        chatMessages.appendChild(waitingDiv);

        // 서버에 /planrecommend/response/ 엔드포인트로 POST 요청 보냄 (JSON 형식 데이터 포함)
        fetch('/planrecommend/response/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ user_query: query })
        })
        .then(response => response.json())
        .then(data => {
            // 기존의 "..." 메시지 삭제
            console.log(data)
            const existingWaitingDiv = document.querySelector('.waiting');
            if (existingWaitingDiv) {
                existingWaitingDiv.remove();
            }

            if (data.error) {
                const errorDiv = document.createElement('div');
                errorDiv.textContent = "서버에서 오류가 발생했습니다: " + data.error;
                errorDiv.className = 'error';  // 오류 메시지에 'error' 클래스 추가
                chatMessages.appendChild(errorDiv);
            } else {
                // 서버에서 반환된 응답
                if (data.message && data.message.trim() !== "") {
                    const answerDiv = document.createElement('div');
                    answerDiv.textContent = data.message;
                    answerDiv.className = 'answer';  // 답변에 'answer' 클래스 추가
                    chatMessages.appendChild(answerDiv);
                } 
                //서버에서 반환된 메시지가 없거나 빈 문자열인 경우에 실행
                else { 
                    const noUpdateDiv = document.createElement('div');
                    noUpdateDiv.textContent = "질문하신 내용의 정보가 업데이트 되지 않았습니다.";
                    noUpdateDiv.className = 'error';  // 오류 메시지에 'error' 클래스 추가
                    chatMessages.appendChild(noUpdateDiv);
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
            const errorDiv = document.createElement('div');
            errorDiv.textContent = "통신 오류가 발생했습니다.";
            errorDiv.className = 'error';  // 오류 메시지에 'error' 클래스 추가
            chatMessages.appendChild(errorDiv);
        });

        // 입력창 초기화
        userInput.value = '';
    }

    // 페이지 로딩 시 자동 질문 전송
    sendQuery(autoQuery);

    // 사용자 입력 처리
    document.getElementById('submitButton').addEventListener('click', function() {
        const userQuery = userInput.value;
        sendQuery(userQuery);
    });
});
