path = r"c:\Users\Owner\Documents\aiadcreate\ai-ads-studio-1\frontend2\notification.html"
text = open(path, encoding="utf-8").read()
marker = 'class="notebar border border-gray-200 rounded-3xl shadow-sm bg-white mt-6 overflow-hidden"'
i = text.find(marker)
if i < 0:
    raise SystemExit("notebar not found")
j = text.find(">", i) + 1
k = text.find("</section>", j)
chunk = text[j:k]
end = j + chunk.rfind("</motion>") if "</motion>" in chunk else j + chunk.rfind("</div>")
replacement = """
              <div id="notifications-list">
                <p class="text-gray-500 text-center py-12 text-sm">Loading notifications...</p>
              </div>
"""
new_text = text[:j] + replacement + text[end:]
open(path, "w", encoding="utf-8").write(new_text)
print("patched", len(text), "->", len(new_text))
