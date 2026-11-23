# AWS CloudOps Learning

Repository để học AWS CloudOps. User sẽ paste transcript bài giảng vào từng phần; nhiệm vụ của Claude là tổng hợp kiến thức thành **một file `index.html` duy nhất**.

## Quy tắc tổng hợp nội dung

- Mỗi transcript mới → **merge vào `index.html` hiện có**, không tạo trang riêng.
- Chia section theo cách hợp lý nhất (theo service / domain), không nhất thiết theo thứ tự transcript. Khi có transcript mới, được phép tái cấu trúc section để giữ mạch logic.
- Mỗi phần nên có:
  - Khái niệm chính & cách hoạt động
  - Con số / giới hạn quan trọng
  - Bảng so sánh khi có nhiều lựa chọn (vd: storage class, loại instance, loại load balancer)
  - Exam tips (SOA-C02/C03) nếu transcript có nhắc
- Chỉ tổng hợp từ nội dung transcript; nếu bổ sung kiến thức ngoài transcript thì đánh dấu rõ (vd: "Ghi chú thêm").
- Con số / tính năng đã đối chiếu với AWS docs mới nhất mà khác bài giảng: ghi giá trị mới, giữ số cũ trong ngoặc ("bài giảng: …"), gắn nhãn `<span class="upd">AWS docs MM/YYYY</span>`.

## Ngôn ngữ

- Nội dung **song ngữ Việt / Anh**: mọi đoạn text (heading, nội dung, bảng, nhãn diagram, exam tips, TOC) đều phải có đủ cả 2 bản.
- `index.html` có **button chuyển đổi VI ⇄ EN** (đặt ở header, dễ thấy). Mặc định tiếng Việt; lựa chọn được nhớ lại qua `localStorage` (bọc try/catch).
- Cách cài đặt: mỗi phần text có 2 phiên bản đánh dấu bằng `lang="vi"` / `lang="en"` (hoặc `data-lang`), chuyển ngôn ngữ bằng cách đổi attribute trên `<html>` và ẩn/hiện bằng CSS — không dùng dịch tự động.
- Khi thêm nội dung mới, luôn viết cả 2 ngôn ngữ cùng lúc; không để sót bản nào.
- Bản tiếng Việt giữ nguyên thuật ngữ AWS bằng tiếng Anh (service name, feature, API, config key...).

## Diagram

- Vẽ diagram bằng **inline SVG** sử dụng **bộ AWS Architecture Icons chính thức** (đúng màu category, đúng group: AWS Cloud, Region, VPC, AZ, subnet...).
- Diagram phải thể hiện đúng cơ chế/luồng thực tế (mũi tên, nhãn rõ ràng), không trang trí suông.
- Diagram hiển thị tốt ở cả light và dark mode.
- Icon được nhúng dạng SVG sprite giữa marker `<!-- ICONS:START -->` / `<!-- ICONS:END -->` trong `index.html`, sinh bởi `tools/build_icons.py` (nguồn: npm package `aws-icons`, bản official AWS Architecture Icons). **Không sửa tay khối sprite.**
  - Dùng icon: `<use href="#ic-<id>" x y width height/>` (danh sách id trong `ICONS` của script).
  - Cần icon mới: thêm vào `ICONS` trong script rồi chạy `python3 tools/build_icons.py`.
- Quy ước SVG diagram: class `.dg`; text 2 ngôn ngữ dùng `<tspan class="vi">` / `<tspan class="en">`; mũi tên dùng class `.ln` (+ `.ok` / `.bad` / `.acc` / `.dash`); group box dùng `.g-cloud`, `.g-region`, `.g-az`, `.g-vpc`, `.g-priv`, `.g-acct`, `.g-asg`, `.g-sg`…
- Sau khi thêm/sửa diagram: chụp screenshot bằng headless Chrome để kiểm tra chữ không bị cắt/đè (cả VI và EN).

## Cấu trúc `index.html`

- Một file tự chứa (self-contained): CSS/JS inline, icon nhúng inline (SVG) — mở trực tiếp bằng trình duyệt không cần server.
- Có sidebar mục lục (TOC) để điều hướng nhanh giữa các section, highlight section đang xem.
- Responsive (đọc được trên điện thoại).
- Hỗ trợ light/dark mode.

## PWA (cài lên iPhone)

- Trang được đóng gói dạng **PWA**: `manifest.webmanifest`, `sw.js` (service worker), `icons/` (nguồn: `icons/icon.svg`).
- `sw.js`: trang (index.html) **network-first** → sửa nội dung xong deploy là app tự nhận bản mới khi có mạng; offline thì dùng bản cache. Chỉ tăng `CACHE` version khi đổi danh sách file `PRECACHE`.
- Giữ tương thích iPhone: dùng biến safe-area (`--st`, `--sl`, `--sr`, `--sbm`) cho phần tử sát mép; không bỏ `viewport-fit=cover`.
- Diagram mới tự có nút ⤢ (viewer toàn màn hình) — chỉ cần đặt trong `<figure class="diagram">`.
- Host trên GitHub Pages (HTTPS bắt buộc cho service worker). Mở file trực tiếp (file://) vẫn chạy nhưng không có offline cache.

