當你向 "https://graph.microsoft.com/v1.0/me/mailfolders/inbox/messages" 發送 GET 請求時，
這個請求將返回你的收件箱中的郵件。除了在 'Authorization' 頭部添加訪問權杖外，
你還可以添加以下一些參數和頭部以獲得更多的控制和功能：

1. **$top：** 這個查詢參數可以用來限制返回的郵件數量。例如，?$top=10 將只返回前 10 封郵件。
2. **$skip：** 這個查詢參數可以用來跳過一定數量的郵件。例如，?$skip=10 將跳過前 10 封郵件。
3. **$filter：** 這個查詢參數可以用來過濾郵件。例如，?$filter=from/emailAddress/address eq 'johndoe@example.com' 將只返回來自 [johndoe@example.com](mailto:johndoe@example.com) 的郵件。
4. **$orderBy：** 這個查詢參數可以用來排序郵件。例如，?$orderBy=receivedDateTime desc 將按照收到的時間降序排序郵件。
5. **$select：** 這個查詢參數可以用來選擇返回的欄位。例如，?$select=subject,receivedDateTime 將只返回每封郵件的主題和收到的時間。
6. **Prefer: outlook.body-content-type="text"：** 這個頭部可以用來控制返回的郵件正文的格式。如果你添加這個頭部並將其值設置為 "text"，則郵件正文將以純文本格式返回。如果你將其值設置為 "html"，則郵件正文將以 HTML 格式返回。

這些只是一些基本的參數和頭部，實際上你可以添加更多的參數和頭部以獲得更多的功能。具體的參數和頭部取決於你的需求和使用的具體 API。你可以查看 Microsoft Graph API 的官方文件來獲得更詳細的信息。