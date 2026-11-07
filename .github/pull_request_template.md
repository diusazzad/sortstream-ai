## Summary of Changes
<!-- সংক্ষেপে লিখুন এই PR-এ কী কাজ করা হয়েছে -->

## Related Issue / Track Milestone
- [x] Theme Track: Rethinking Waste (Arbiter Hacks V1)
- [ ] General Track

## Changes Implemented
- [ ] নতুন এপিআই এন্ডপয়েন্ট বা ইঞ্জিন মডিউল
- [ ] গাণিতিক ও EPA WARM v16 বিজনেস লজিক
- [ ] ইউনিট টেস্ট যুক্ত করা হয়েছে (Pytest)
- [ ] ডকস্ট্রিং বা ডকুমেন্টেশন আপডেট

## Verification Checklist (Reviewer QA)
- [ ] **Domain & Math Verification:** ইউনিট কনভার্সন (grams -> kg -> metric tons) এবং কার্বন সূত্র $\Delta E_{\text{net}} = \sum_{m} M_m \times (EF_{\text{landfill}, m} - EF_{\text{recycle}, m})$ নির্ভুল
- [ ] **Edge Cases:** $0$ কাউন্ট, অপ্রত্যাশিত মেটেরিয়াল টাইপ এবং নেগেটিভ সংখ্যা হ্যান্ডেল করা হয়েছে
- [ ] **Code Cleanliness:** টাইপ হিন্টিং (Pydantic v2 schemas), নো হার্ডকোডেড সিক্রেটস
- [ ] **Test Coverage:** সব ইউনিট টেস্ট পাস করেছে (`pytest backend/tests/`)
- [ ] **Performance:** কোনো দীর্ঘস্থায়ী ব্লকিং অপারেশন বা মেমরি লিক নেই

## How to Test
```bash
cd backend
pip install -r requirements.txt
pytest -v tests/
```
