# twitch-clip-archive
단일 스트리머용 트위치 클립 백엔드리스 아카이빙 웹 시스템<br/>
(twitch clip archiving backendless web system for a single streamer)

# 사용방법
- `build.py` 를 실행하여 `origin.json` 파일과 clips 동영상과 썸네일을 다운로드 받습니다. (실패 시 다시 실행해주세요.)
- 이제 `index.html`로 직접 아카이브된 클립들을 확인할 수 있습니다.

# 동작화면
![sample](sample.gif)
> 개인정보 노출을 최소화하기 위해 임의로 모자이크 처리하였습니다. 양해 바랍니다.

# 안내사항
해당 시스템은 별도로 동영상 및 썸네일을 다운받지 않고도 `origin.json`을 개별적으로 사용하여 사용하실 수 있습니다.
다만, 썸네일과 동영상 호출에서 과도한 네트워크 트래픽 발생으로 인하여 차단 당하실 수 있으니 주의 바랍니다.