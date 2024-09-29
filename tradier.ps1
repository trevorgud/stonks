$headers = @{
    Authorization = "Bearer <token>"
    Accept        = "application/json"
}

Invoke-RestMethod -Uri "https://api.tradier.com/v1/user/profile" -Method Get -Headers $headers

$response | ConvertTo-Json -Depth 10
