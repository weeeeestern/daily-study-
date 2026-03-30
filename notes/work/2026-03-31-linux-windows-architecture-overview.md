STATUS: TODO
DATE: 2026-03-31
TOPIC_ID: linux-windows-architecture-overview

# Linux vs Windows Architecture Overview

## 오늘의 목표
이 주제를 읽고, Linux와 Windows의 차이를 단순 암기가 아니라 자기 언어로 설명할 수 있어야 한다.

## 핵심 개념 설명
### 주제 개요
Compare the overall operating system architecture of Linux and Windows, focusing on design philosophy, layering, and how user space and kernel space are organized.

### Linux 관점 자세히
Monolithic kernel with modular components, Unix heritage, userland and kernel separation, configurable distributions.

이 부분에서는 Linux/Unix 계열의 설계 철학, 실제 운영 방식, 그리고 명령줄·관리 도구와의 연결까지 생각해보면 좋다. 단순히 기능 차이를 외우기보다, 왜 이런 구조가 자연스럽게 자리잡았는지까지 설명할 수 있어야 한다.

### Windows 관점 자세히
Hybrid kernel design, NT architecture, subsystem model, tighter integration between core components and platform services.

이 부분에서는 Windows NT 계열의 설계, GUI 중심 사용자 경험, 엔터프라이즈 관리 방식, 그리고 Microsoft 생태계와의 결합이 어떤 영향을 주는지 함께 보면 좋다.

### 비교 포인트
- 두 운영체제가 같은 문제를 어떻게 다르게 푸는가
- 설계 차이가 실제 관리자 경험에 어떤 차이를 만드는가
- 보안, 유지보수, 자동화 관점에서 어떤 장단점이 있는가

### 왜 중요한가
이 주제는 단순 기능 비교가 아니라, 운영체제의 철학과 관리 방식 차이를 이해하는 핵심 축이다. 이걸 이해하면 파일 시스템, 프로세스, 서비스, 보안, 업데이트 같은 후속 주제도 더 잘 연결된다.

## 꼭 알아야 할 것
- 이 주제의 핵심 개념을 정의할 수 있어야 함
- Linux 쪽 구현/철학을 설명할 수 있어야 함
- Windows 쪽 구현/철학을 설명할 수 있어야 함
- 두 시스템의 차이가 왜 생겼는지 추론할 수 있어야 함
- 실무적으로 어떤 차이를 만드는지 연결해서 말할 수 있어야 함

## 오늘의 질문
1. Linux vs Windows Architecture Overview 주제를 자기 언어로 설명해보세요.
2. Linux와 Windows가 이 문제를 다르게 푸는 이유를 설계 관점에서 비교해보세요.
3. 이 차이가 실제 사용, 관리, 성능, 보안, 운영 경험에 어떤 영향을 주는지 설명해보세요.
4. 처음 배우는 사람에게 이 주제를 설명한다면 어떤 흐름으로 설명할지 적어보세요.

## 실습 또는 관찰 포인트
Draw a simple layered diagram of both systems and explain the role of kernel, drivers, services, and user applications.

## 참고 자료
- https://learn.microsoft.com/en-us/windows-hardware/drivers/gettingstarted/architecture-of-the-windows-kernel
- https://www.kernel.org/doc/html/latest/admin-guide/overview.html

## My Answer


## Review
- 말랑이 피드백 대기

## Final Notes

