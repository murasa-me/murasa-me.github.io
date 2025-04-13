// This file contains the main JavaScript logic for the application.
// It includes DOM manipulation and event listener setup.

document.addEventListener('DOMContentLoaded', () => {
    // Your code here
    console.log('DOM fully loaded and parsed');
});

// 入力値の保持
window.onload = function () {
  document.getElementById("narouInput").value = localStorage.getItem("narouInput") || "";
  document.getElementById("xidInput").value = localStorage.getItem("xidInput") || "";
};

function fetchNovels(apiUrl, callback) {
  const cbName = "cb" + Math.random().toString(36).substring(2);
  window[cbName] = function(data) {
    callback(data);
    delete window[cbName];
    document.body.removeChild(script);
  };
  const script = document.createElement("script");
  script.src = apiUrl + "&callback=" + cbName;
  document.body.appendChild(script);
}

function loadData(source) {
  const status = document.getElementById("status");
  status.textContent = "データ取得中...";

  const id = source === "narou" ? document.getElementById("narouInput").value.trim() : document.getElementById("xidInput").value.trim();
  if (!id) {
    status.textContent = "IDを入力してください。";
    return;
  }

  // 入力キャッシュ
  localStorage.setItem(source === "narou" ? "narouInput" : "xidInput", id);

  const param = source === "narou" ? `userid=${id}` : `xid=${id}`;
  const base = source === "narou" ? "https://api.syosetu.com/novelapi/api/?" : "https://api.syosetu.com/novel18api/api/?";
  const apiUrl = base + param + "&out=jsonp";

  fetchNovels(apiUrl, function(data) {
    const novels = data.filter(n => n.title);
    if (novels.length === 0) {
      status.textContent = "取得に失敗しました。入力しているIDを確認してください。";
    } else {
      displayNovels(novels, source);
    }
  });
}

function displayNovels(novels, source) {
  const container = document.getElementById("novelTables");
  const usernameHeader = document.getElementById("usernameHeader");
  const status = document.getElementById("status");
  container.innerHTML = "";
  status.textContent = "";

  const now = new Date().toLocaleString();
  const lastFetch = localStorage.getItem("lastFetchTime") || "なし";
  localStorage.setItem("lastFetchTime", now);

  novels.forEach(novel => {
    const prevCache = JSON.parse(localStorage.getItem(novel.ncode) || "{}");
    localStorage.setItem(novel.ncode, JSON.stringify(novel));

    const table = document.createElement("table");
    table.className = "table table-bordered table-striped table-hover mb-5";

    let html = "";

    html += `<tr>
      <th colspan="3"><a href='https://ncode.syosetu.com/${novel.ncode.toLowerCase()}/' target='_blank'>${novel.title}</a></th>
    </tr>`;
    html += `<tr class='col-3'><th rowspan="2">取得時間</th><th>前回</th><th>今回</th></tr>`;
    html += `<tr class='col-3'><th>${lastFetch}</th><th>${now}</th></tr>`;
    html += `<tr class='col-3'><th>指標</th><th>前回値</th><th>今回値</th></tr>`;

    const fields = [
      { key: "length", label: "作品文字数" },
      { key: "impression_cnt", label: "感想数" },
      { key: "review_cnt", label: "レビュー数" },
      { key: "global_point", label: "総合評価ポイント" },
      { key: "all_hyoka_cnt", label: "評価者数" },
      { key: "all_point", label: "評価pt" },
      { key: "fav_novel_cnt", label: "ブクマ数" },
      { key: "daily_point", label: "日間pt" },
      { key: "weekly_point", label: "週間pt" },
      { key: "monthly_point", label: "月間pt" },
      { key: "quarter_point", label: "四半期pt" },
      { key: "yearly_point", label: "年間pt" }
    ];

    fields.forEach(({ key, label }) => {
      const prev = prevCache[key] ?? "-";
      const curr = novel[key] ?? "-";
      let cls = "";
      if (prev !== "-" && curr !== "-" && !isNaN(prev) && !isNaN(curr)) {
        if (Number(curr) > Number(prev)) cls = "highlight";
        else if (Number(curr) < Number(prev)) cls = "lowlight";
      }
      html += `<tr class='col-3'><td>${label}</td><td>${prev}</td><td class='${cls}'>${curr}</td></tr>`;
    });

    table.innerHTML = html;
    container.appendChild(table);
  });

  const username = novels[0].writer || "不明";
  usernameHeader.textContent = `${username} さんの小説評価`;
}

function shareOnTwitter() {
    const pageTitle = document.title;
    const pageUrl = window.location.href;
    const tweetText = encodeURIComponent(`${pageTitle} ${pageUrl}`);
    const twitterUrl = `https://twitter.com/intent/tweet?text=${tweetText}`;
    window.open(twitterUrl, "_blank");
  }
