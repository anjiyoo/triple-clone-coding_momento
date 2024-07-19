document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('submitButton').addEventListener('click', function() {
        var userQuery = document.getElementById('userInput').value;
        if (!userQuery.trim()) {
            // 입력 필드가 비어있을 경우 메시지 표시
            document.getElementById('chat-messages').innerText = "질문을 입력해주세요.";
            return; // 함수 실행 중지
        }

        // 채팅창에 사용자 입력 바로 표시
        var chatMessages = document.getElementById('chat-messages');
        var questionDiv = document.createElement('div');
        questionDiv.textContent = userQuery;
        questionDiv.className = 'question';  // 질문에 'question' 클래스 추가
        chatMessages.appendChild(questionDiv);

        // 서버 응답을 기다리는 동안의 메시지
        var waitingDiv = document.getElementById('waiting');
        var questionDiv = document.createElement('div');
        waitingDiv.textContent = "...";
        waitingDiv.className = 'waiting';  // 대기 메시지에 'waiting' 클래스 추가
        chatMessages.appendChild(waitingDiv);

        // 서버에 /chatbot/response/ 엔드포인트로 POST 요청 보냄 (JSON 형식 데이터 포함)
        fetch('/chatbot/response/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ user_query: userQuery })
        })
        .then(response => response.json())
        .then(data => {
            // 기존의 "..." 메시지 삭제
            var waitingDiv = document.querySelector('.waiting');
            if (waitingDiv) {
                waitingDiv.remove();
            }

            if (data.error) {
                document.getElementById('chat-messages').innerText = "서버에서 오류가 발생했습니다: " + data.error;
            } else {
                // 서버에서 반환된 응답
                if (data.message && data.message.trim() !== "") {
                    const answerDiv = document.createElement('div');
                    answerDiv.textContent = data.message;
                    answerDiv.className = 'answer';  // 답변에 'answer' 클래스 추가
                    document.getElementById('chat-messages').appendChild(answerDiv);
                } 
                //서버에서 반환된 메시지가 없거나 빈 문자열인 경우에 실행
                else { 
                    document.getElementById('chat-messages').innerText = "질문하신 내용의 정보가 업데이트 되지 않았습니다.";
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('chat-messages').innerText = "통신 오류가 발생했습니다.";
        });

        // 입력창 초기화
        document.getElementById('userInput').value = '';
    });
});


// 챗봇 메인 화면 검색예시 버튼
function addQuestion(question) {
    document.getElementById('userInput').value = question;
}