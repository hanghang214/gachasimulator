// 获取相关元素
const slider = document.querySelector('.image-slider');
const prevButton = document.querySelector('.prev-btn');
const nextButton = document.querySelector('.next-btn');

// 图片的索引
let currentIndex = 0;

// 设置按钮点击事件
prevButton.addEventListener('click', () => {
  currentIndex = (currentIndex - 1 + slider.children.length) % slider.children.length;
  updateSliderPosition();
});

nextButton.addEventListener('click', () => {
  currentIndex = (currentIndex + 1) % slider.children.length;
  updateSliderPosition();
});

// 更新图片滑动位置
function updateSliderPosition() {
  const slideWidth = slider.offsetWidth;
  const offset = -currentIndex * slideWidth;
  slider.style.transform = `translateX(${offset}px)`;
}
