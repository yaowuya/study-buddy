---
name: Soft Organic Cards
colors:
  surface: '#fcf8f8'
  surface-dim: '#dcd9d9'
  surface-bright: '#fcf8f8'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f6f3f3'
  surface-container: '#f1eded'
  surface-container-high: '#ebe7e7'
  surface-container-highest: '#e5e2e2'
  on-surface: '#1c1b1c'
  on-surface-variant: '#45474a'
  inverse-surface: '#313030'
  inverse-on-surface: '#f3f0f0'
  outline: '#75777b'
  outline-variant: '#c5c6cb'
  surface-tint: '#5c5e63'
  primary: '#000000'
  on-primary: '#ffffff'
  primary-container: '#191c20'
  on-primary-container: '#818489'
  inverse-primary: '#c5c6cc'
  secondary: '#3a692e'
  on-secondary: '#ffffff'
  secondary-container: '#b7eea5'
  on-secondary-container: '#3e6e32'
  tertiary: '#000000'
  on-tertiary: '#ffffff'
  tertiary-container: '#211a13'
  on-tertiary-container: '#8d8278'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#e1e2e8'
  primary-fixed-dim: '#c5c6cc'
  on-primary-fixed: '#191c20'
  on-primary-fixed-variant: '#44474c'
  secondary-fixed: '#baf1a7'
  secondary-fixed-dim: '#9fd58d'
  on-secondary-fixed: '#012200'
  on-secondary-fixed-variant: '#225119'
  tertiary-fixed: '#eee0d4'
  tertiary-fixed-dim: '#d1c4b9'
  on-tertiary-fixed: '#211a13'
  on-tertiary-fixed-variant: '#4e453c'
  background: '#fcf8f8'
  on-background: '#1c1b1c'
  surface-variant: '#e5e2e2'
  background-alt: '#F8F9FB'
  text-secondary: '#6B7280'
  soft-lilac: '#E5D9F2'
  pale-peach: '#FFE4D6'
typography:
  display-num:
    fontFamily: Inter
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  display-num-mobile:
    fontFamily: Inter
    fontSize: 36px
    fontWeight: '700'
    lineHeight: 44px
    letterSpacing: -0.02em
  headline-h1:
    fontFamily: Inter
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 36px
  headline-h1-mobile:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-h2:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '500'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gap-xs: 0.5rem
  gap-sm: 1rem
  gap-md: 1.5rem
  container-margin: 1.5rem
  card-padding: 1.25rem
---

# Stitch Design System: Soft Organic Cards
## 1. 概述 (Overview)
Stitch 的 UI 风格采用了 **"Soft Organic Cards" (柔和有机卡片风)**。该风格旨在通过柔和的低饱和色彩、流畅的有机形状和大圆角卡片，为用户提供轻松、现代且友好的操作体验。界面需要在保持高可用性和清晰数据层级的同时，消除传统金融/Token管理工具的冰冷感。
---
## 2. 色彩系统 (Color Palette)
色彩是该风格的核心，主要依赖大量留白与马卡龙色系的色块进行对比。
### 基础色 (Base Colors)
* **Background (主背景):** `#F8F9FB` (极其浅的冷灰色/米白色，提供干净的画布)
* **Surface (卡片背景):** `#FFFFFF` (纯白，用于承载主要信息)
* **Text Primary (主标题/数字):** `#111418` (近黑色，确保高对比度与易读性)
* **Text Secondary (副标题/描述):** `#6B7280` (中灰色)
### 品牌/点缀色 (Accent & Pastel Colors)
用于卡片背景、标签、图标底色或高亮区域：
* **Mint Green (薄荷绿):** `#B9F0A6` (常用于积极操作、成功状态或主要高亮)
* **Soft Lilac (浅紫):** `#E5D9F2` (用于分类、中性标签或次要模块)
* **Pale Peach/Orange (柔和橘):** `#FFE4D6` (用于警告、特殊标记或插画背景)
---
## 3. 字体排版 (Typography)
排版需要现代、干净，强调数据的层级关系。推荐使用 **San Francisco (iOS)**, **Inter**, 或 **Roboto** 等无衬线字体。
* **Display / 数字 (Tokens/金额):** `36px` - `48px`, **Bold (粗体)**. 突出核心数据。
* **H1 (页面标题):** `24px` - `28px`, **Semi-Bold**. 例如 "My Tokens", "View transactions"。
* **H2 (卡片标题):** `16px` - `18px`, **Medium**. 例如 "Bas van der gught"。
* **Body (正文/辅助信息):** `12px` - `14px`, **Regular**. 用于时间戳、细微说明。
---
## 4. 形状与组件 (Shapes & Components)
### 卡片 (Cards)
* **圆角 (Border Radius):** 使用大圆角，标准卡片推荐使用 `20px` - `24px` 的圆角。
* **阴影 (Shadows):** 极度柔和且范围广的弥散阴影。避免生硬的黑影。
    * *示例 CSS:* `box-shadow: 0 12px 24px rgba(0, 0, 0, 0.04);`
* **有机形状 (Organic Blobs):** 在卡片内部（如 "Event details" 顶部），使用不规则的波浪形或有机形状作为背景，打破传统矩形的死板。
### 按钮 (Buttons)
* **Primary Action (主操作):** 胶囊形状 (Pill-shaped)，高度 `44px` - `48px`，完全圆角 (`border-radius: 500px`)。通常使用黑色背景和白色文字以吸引注意力。
* **Icon Buttons (图标按钮):** 圆形 (`border-radius: 50%`)，带有一点灰色背景或轻微阴影，用于扫码 (Scan)、设置或更多选项 (`...`)。
### 导航 (Navigation)
* **底部浮动操作栏 (Floating Bottom Bar):** 采用悬浮式胶囊设计，内部包含图标。当前选中项使用明亮的底色（如薄荷绿）高亮，未选中项保持黑白简约。
---
## 5. 布局与间距 (Layout & Spacing)
* **留白 (Whitespace):** 保持呼吸感。模块之间保持至少 `16px` - `24px` 的间距。
* **模块化 (Modularity):** 信息必须被包裹在各自独立的视觉容器（卡片或彩色背景）中，避免信息直接散落在背景上。
---
## 6. 图标与视觉元素 (Icons & Imagery)
* **图标风格:** 2D 扁平化、线条粗细均匀的线性图标或填充图标，风格需圆润。
* **头像 (Avatars):** 圆形裁切，对于没有照片的实体，使用带有相关马卡龙背景色的图标（如黑色的双手图标搭配粉色背景）。