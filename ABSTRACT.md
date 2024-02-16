The authors introduce the **NAO: Natural Adversarial Object Dataset**, to evaluate the robustness of object detection models. NAO contains 7,934 images and 
9, 43 objects that are unmodified and representative of real-world scenarios, but cause state-of-the-art detection models to misclassify with high confidence. The mean average precision (mAP) of EfficientDet-D7 drops 74.5% when evaluated on NAO compared to the standard MSCOCO validation set.

## Motivation

It's becoming increasingly common for machine learning vision models to excel on large-scale training sets and generalize well on canonical test sets from the same distribution. However, they still struggle with generalizing towards challenging, out-of-distribution samples. Relying solely on model performance on canonical test sets can be misleading, as it often overestimates their effectiveness on new data. Recent research on adversarial attacks has revealed deep neural networks' surprising vulnerability to artificially manipulated images, raising concerns about their efficacy and security.

While it's well-known that neural networks are susceptible to adversarial attacks designed to deceive the system, such attacks typically assume control over the raw input or access to the model weights. However, it's important to recognize that real-world, unaltered images can also be adversarially leveraged to cause models to fail. These "natural" adversarial attacks pose a less constrained threat model, enabling attackers to create black-box attacks using readily available, naturally occurring images. Such images, termed natural adversarial examples, are unmodified real-world images that prompt modern image classification models to make severe, high-confidence errors.

## Dataset description

In the realm of natural adversarial examples, the focus has predominantly been on constructing challenges for image classification models. However, the authors of this study aim to develop an evaluation set tailored specifically for object detection tasks. They introduce a dataset named Natural Adversarial Objects (NAO) designed to assess the worst-case performance of cutting-edge object detection models. Notably, NAO emphasizes the inclusion of unmodified, real-world examples. The authors propose a methodology for identifying natural adversarial objects, leveraging both existing object detection models and human annotators. Initially, they assess predictions from various pre-existing detection models against a dataset already annotated with ground truth bounding boxes. Images featuring high-confidence false positives and misclassified objects are earmarked as potential candidates for NAO. Subsequently, a human annotation pipeline is employed to sift through mislabeled images and identify non-obvious objects, such as occluded or blurry items. Finally, the images are re-annotated using the object categories outlined in the [MSCOCO](https://cocodataset.org/#home) dataset.

<img src="https://github.com/dataset-ninja/nao/assets/120389559/14df22d6-6fc8-4faa-9181-e4e9adaa6ef6" alt="image" width="1200">

<span style="font-size: smaller; font-style: italic;">Sample images from NAO where EfficientDet-D7 produces high confidence false positives and egregious classification. Left: High confidence misclassified objects where the ground truth label is in distribution and among the MSCOCO object categories. Right: High confidence false positives where the ground truth object is out-of-distribution (i.e. not part of MSCOCO object categories). The misclassified objects and false positives are superficially similar to the predicted classes – for example, the fin of the shark is visually similar to the airplane tail and the yellow petals of the flower are similar to a bunch of bananas.</span>

To create NAO, the authors first sourced images from the training set of [OpenImages](https://storage.googleapis.com/openimages/web/index.html), a large, annotated image dataset containing approximately 1.9 million images and 15.8 million bounding boxes across 600 object classes. After obtaining a set of natural adversarial images, the authors exhaustively annotate the images with all 80 MSCOCO object classes to facilitate straightforward comparison between NAO and the MSCOCO val and test sets. 

## Annotation process

The authors annotation process has two annotation stages: classification and bounding box annotation.

* **Classification stage.** In the classification stage, annotators identify whether the object described by the bounding box shown indeed belongs to the ground truth class as defined by the annotation in OpenImages or as predicted by the EfficientDet-D7. The purpose of this stage is to remove the possibility that the model prediction is "incorrect" due to the ground truth label being incorrect. In addition, they ask the annotators to confirm whether the object can be "obviously classified" according to the following criteria:
1. Is the bounding box around the object correctly sized and positioned such that it is not too big or too small?
2. Does the object appear blurry?
3. Is the object occluded (i.e. are there other objects in front of this one)?
4. Is the object a depiction of the correct class (such as a drawing or an image on a billboard)?

The authors asked these additional questions to filter out ambiguous objects, such that a human can easily identify what class an object belongs to. After this filtering, 18.1% of the images (7,934) remain; each of the remaining images are confirmed to fulfill the 4 criteria, and represent true misclassifivations by the model. In this first annotation stage (classification), 5 different annotators are asked to annotate the same image and the authors use their consensus to produce an aggregated response by majority vote.

* **Bounding box stage.** Annotators exhaustively identify and put boxes around all objects that belong to the MSCOCO object categories. The authors are unable to directly use the annotations from OpenImages because there is not a one-to-one mapping between the OpenImages and MSCOCO object categories, and because the bounding box annotations from OpenImages are not exhaustively annotated. These bounding box annotation tasks are completed by 2 sets of annotators. The first set of annotators complete the bulk of the task by placing bounding boxes around objects that belong to the MSCOCO object categories. The second set of annotators review the work of the first set of annotators, sometimes adding missing bounding boxes or editing the existing ones. To ensure the quality of the annotation is high, in both of these stages, the annotators have to pass multiple quizzes before they can start working tasks to ensure they understand the instructions well. If the annotator fails to maintain a good score, they are no longer eligible to continue to annotate the images. When the annotators from the 2 different stages disagree, the authors tie break by choosing second annotator who is positioned as the reviewer.

<img src="https://github.com/dataset-ninja/nao/assets/120389559/36d8054a-847a-4b07-981f-fbd6a6a63a40" alt="image" width="600">

<span style="font-size: smaller; font-style: italic;">Top: Annotation interface for the first annotation stage (classification) where the annotator confirms that the object belongs to the correct category, not occluded, not blurry and not a depiction. Bottom: Annotation interface for second annotation stage (bounding box) where the annotators locate and classify all objects in the images using the MSCOCO object categories.</span>

| Statistics     |Number of Images | Number of Objects | 1st Object | 2nd Object | 3rd Object |
|----------------|-----------------|-------------------|------------|------------|------------|
| MSCOCO val     |5,000            | 36,781            | Person     | Car        | Chair      |
|                |                 |                   | (11,004)   | (1,932)    | (1,791)    |
| MSCOCO test-dev|20,288           | -                 | -          | -          | -          |
| NAO            |7,934            | 9,943             | Person     | Cup        | Car        |
|                |                 |                   | (3,551)    | (1,366)    | (707)      |

<span style="font-size: smaller; font-style: italic;">Dataset statistics of MSCOCO val, test-dev and NAO.</span>



