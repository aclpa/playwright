성능 지표 심층 분석
https://docs.ultralytics.com/ko/guides/yolo-performance-metrics/#introduction
Precision(정밀도)-Recall(재현율) 그래프
![precision](/media/precision.png)

Intersection over Union (IoU): IoU는 예측된 bounding box와 ground truth bounding box 간의 겹침을 정량화하는 척도입니다. 객체 localization의 정확성을 평가하는 데 기본적인 역할을 합니다.

평균 정밀도 (AP): AP는 정밀도-재현율 곡선 아래 면적을 계산하여 모델의 정밀도 및 재현율 성능을 통합하는 단일 값을 제공합니다.

Mean Average Precision (mAP): mAP는 여러 객체 클래스에 걸쳐 평균 AP 값을 계산하여 AP 개념을 확장합니다. 이는 모델 성능에 대한 포괄적인 평가를 제공하기 위해 다중 클래스 객체 detect 시나리오에서 유용합니다.

정밀도 및 재현율: 정밀도는 모든 양성 예측 중에서 참 양성의 비율을 정량화하여 오탐지를 피하는 모델의 능력을 평가합니다. 반면에 재현율은 모든 실제 양성 중에서 참 양성의 비율을 계산하여 클래스의 모든 인스턴스를 detect하는 모델의 능력을 측정합니다.

P (정밀도): 감지된 객체의 정확도로, 얼마나 많은 감지가 올바른지 나타냅니다.

R (재현율): 이미지에서 객체의 모든 인스턴스를 식별하는 모델의 기능입니다.

mAP50: IoU(Intersection over Union) 임계값 0.50에서 계산된 평균 정밀도입니다. 이는 '쉬운' detect만 고려한 모델의 정확도 측정값입니다.

이 AI 모델은 정답 박스와 50% 이상 겹쳤을 때를 정답으로 쳐주면, 모든 UI 요소들을 종합적으로 찾아내는 능력이 평균 74.8점(0.748)입니다

F1 = 2 × (Precision × Recall) / (Precision + Recall)

![confidence](/media/confidence.png)
