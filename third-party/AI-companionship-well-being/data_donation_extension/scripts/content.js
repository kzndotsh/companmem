(() => {
  const extAPI = chrome;
  const extVersion = "1.1.3";

  const metadata = {
    version: 1,
    created: Date.now(),
    modified: Date.now(),
    source: null,
    tool: {
      name: "Character.AI Data Donation Tool",
      version: extVersion,
    },
  };

  // xhook + wsHook
  try {
    const intercept_lib__url = extAPI.runtime.getURL("scripts/intercept.js");
    const interceptHookScript = document.createElement("script");
    interceptHookScript.crossOrigin = "anonymous";
    interceptHookScript.id = "xhook";
    interceptHookScript.onload = function () {};
    interceptHookScript.src = intercept_lib__url;
    const firstScript = document.getElementsByTagName("script")[0];
    firstScript.parentNode.insertBefore(interceptHookScript, firstScript);
  } catch (e) {
    console.warn("[cai-tools] failed to inject intercept.js:", e);
  }

  handleLocationChange(null, { lastHref: "" });
  function handleLocationChange(_m, observer) {
    if (window.location.href !== observer.lastHref) {
      observer.lastHref = window.location.href;
      cleanDOM();
      const location = getPageType();
      if (
        location === "character.ai/chat" ||
        location.includes(".character.ai/chat2") ||
        (location.includes(".character.ai/chat") && getCharId())
      ) {
        initialize_caitools();
      }
    }
  }

  const locationObserver = new MutationObserver(handleLocationChange);
  locationObserver.lastHref = window.location.href;
  locationObserver.observe(document, {
    childList: true,
    attributes: false,
    subtree: true,
    characterData: false,
  });

  // Reveal memory text
  document.addEventListener("click", (e) => {
    const el = e.target;
    if (el.matches('a[href="#-"], a[title]') && el.textContent === "-") {
      e.preventDefault();
      el.textContent = el.getAttribute("title");
      el.dataset.revealed_memory = true;
    } else if (el.dataset.revealed_memory) {
      e.preventDefault();
    }
  });

  function handleProgressInfo(text) {
    const progressInfo = document.querySelector(
      ".cai_tools-cont .cait_progressInfo"
    );
    if (progressInfo) progressInfo.textContent = text;
  }
  function handleProgressInfoHist(text) {
    const progressInfo = document.querySelector(
      ".cai_tools-cont .cait_progressInfo_Hist"
    );
    if (progressInfo) progressInfo.textContent = text;
  }

  function cleanDOM() {
    document.querySelectorAll('[data-tool="cai_tools"]').forEach((element) => {
      element.remove();
    });
  }

  function applyConversationMeta(converExtId, newSimplifiedChat) {
    const sel = `meta[cai_converExtId="${converExtId}"]`;
    const meta =
      document.querySelector(sel) ||
      (() => {
        const m = document.createElement("meta");
        m.setAttribute("cai_converExtId", converExtId);
        document.head.appendChild(m);
        return m;
      })();
    meta.setAttribute("cai_conversation", JSON.stringify(newSimplifiedChat));
    handleProgressInfo("(Ready!)");
    console.log("FINISHED", newSimplifiedChat);
  }

  async function safeFetchJson(url, opts = {}) {
    try {
      const res = await fetch(url, opts);
      if (!res.ok) {
        return { ok: false, status: res.status, data: null };
      }
      const data = await res.json().catch(() => null);
      return { ok: true, status: 200, data };
    } catch (e) {
      return { ok: false, status: 0, data: null };
    }
  }

  async function resolveCharacterData(charId, AccessToken) {
    const headers = {
      Accept: "application/json",
      "Content-Type": "application/json",
    };
    if (AccessToken) headers.authorization = AccessToken;

    if (AccessToken) {
      const r = await safeFetchJson(
        `https://neo.character.ai/characters/${charId}`,
        { method: "GET", headers }
      );
      const c = r.data?.character ?? r.data;
      if (r.ok && c) {
        return {
          name: c.name ?? null,
          avatar_file_name: c.avatar_file_name ?? c.avatar_rel_path ?? null,
          description: c.description ?? null,
          greeting: c.greeting ?? c.first_mes ?? null,
          raw: c,
        };
      }
    }

    if (AccessToken) {
      const r = await safeFetchJson(
        `https://neo.character.ai/chats/?character_ids=${encodeURIComponent(
          charId
        )}&num_preview_turns=0`,
        { method: "GET", headers }
      );
      if (r.ok && Array.isArray(r.data?.chats) && r.data.chats.length) {
        const cc = r.data.chats[0].character || r.data.chats[0].char || null;
        if (cc) {
          return {
            name: cc.name ?? null,
            avatar_file_name: cc.avatar_file_name ?? cc.avatar_rel_path ?? null,
            description: cc.description ?? null,
            greeting: cc.greeting ?? cc.first_mes ?? null,
            raw: cc,
          };
        }
      }
    }

    try {
      const nextScript =
        document.getElementById("__NEXT_DATA__") ||
        Array.from(
          document.querySelectorAll('script[type="application/json"]')
        ).find((s) => s.id === "__NEXT_DATA__");
      if (nextScript?.textContent) {
        const nd = JSON.parse(nextScript.textContent);
        const c6 =
          nd?.props?.pageProps?.character ||
          nd?.props?.pageProps?.entity?.character ||
          nd?.props?.pageProps?.data?.character ||
          null;
        if (c6) {
          return {
            name: c6.name ?? null,
            avatar_file_name: c6.avatar_file_name ?? c6.avatar_rel_path ?? null,
            description: c6.description ?? null,
            greeting: c6.greeting ?? c6.first_mes ?? null,
            raw: c6,
          };
        }
      }
    } catch {}

    try {
      const headerName = document
        .querySelector(
          "[data-testid='header-primary'] [data-testid='characterName']"
        )
        ?.textContent?.trim();
      if (headerName) {
        return {
          name: headerName,
          avatar_file_name: null,
          description: null,
          greeting: null,
          raw: { name: headerName },
        };
      }
    } catch {}

    return {
      name: null,
      avatar_file_name: null,
      description: null,
      greeting: null,
      raw: {},
    };
  }
  const fetchMessagesLegacy = async ({
    AccessToken,
    nextPage,
    converExtId,
    chatData,
    fetchDataType,
  }) => {
    await new Promise((resolve) => setTimeout(resolve, 200));
    let url = `https://plus.character.ai/chat/history/msgs/user/?history_external_id=${converExtId}`;
    if (nextPage > 0) url += `&page_num=${nextPage}`;

    try {
      const res = await fetch(url, {
        method: "GET",
        headers: { authorization: AccessToken },
      });
      if (res.ok) {
        const data = await res.json();
        chatData.turns = [...data.messages, ...chatData.turns];

        if (data.has_more == false) {
          const newSimplifiedChat = [];
          chatData.turns
            .filter((m) => m.is_alternative == false && m.src__name != null)
            .forEach((msg) =>
              newSimplifiedChat.push({
                name: msg.src__name,
                message: msg.text,
                isHuman: msg.src__is_human,
              })
            );

          if (fetchDataType === "conversation") {
            applyConversationMeta(converExtId, newSimplifiedChat);
          } else if (fetchDataType === "history") {
            chatData.history = newSimplifiedChat;
            chatData.turns = [];
          }
          return;
        }

        await fetchMessagesLegacy({
          AccessToken,
          nextPage: data.next_page,
          converExtId,
          chatData,
          fetchDataType,
        });
      } else if (res.status === 429) {
        console.log("Rate limiting. Retry in 10s.");
        await new Promise((r) => setTimeout(r, 10000));
        return await fetchMessagesLegacy({
          AccessToken,
          nextPage,
          converExtId,
          chatData,
          fetchDataType,
        });
      } else {
        console.warn("[legacy] non-ok", res.status, "— skipping legacy fetch.");
      }
    } catch (error) {
      console.warn("[legacy] error; skipping legacy fetch.", error);
    }
  };

  const fetchMessagesChat2 = async ({
    AccessToken,
    nextToken,
    converExtId,
    chatData,
    fetchDataType,
  }) => {
    await new Promise((resolve) => setTimeout(resolve, 200));
    let url = `https://neo.character.ai/turns/${converExtId}/`;

    try {
      const res = await fetch(
        url + (nextToken ? `?next_token=${nextToken}` : ""),
        {
          method: "GET",
          headers: { authorization: AccessToken },
        }
      );
      if (res.ok) {
        const data = await res.json();
        if (data.meta.next_token == null) {
          const newSimplifiedChat = [];
          chatData.turns.forEach((msg) => {
            try {
              const last = msg.candidates[msg.candidates.length - 1];
              newSimplifiedChat.push({
                name: msg.author?.name,
                message: last?.raw_content ?? "",
                isHuman: !!msg.author?.is_human,
              });
            } catch (e) {
              console.warn("[chat2] malformed turn:", msg, e);
            }
          });
          newSimplifiedChat.reverse();

          if (fetchDataType === "conversation") {
            applyConversationMeta(converExtId, newSimplifiedChat);
          } else if (fetchDataType === "history") {
            chatData.history = newSimplifiedChat;
            chatData.turns = [];
          }
          return;
        }

        chatData.turns = [...chatData.turns, ...data.turns];

        await fetchMessagesChat2({
          AccessToken,
          nextToken: data.meta.next_token,
          converExtId,
          chatData,
          fetchDataType,
        });
      } else if (res.status === 429) {
        console.log("Rate limiting. Retry in 10s.");
        await new Promise((r) => setTimeout(r, 10000));
        return await fetchMessagesChat2({
          AccessToken,
          nextToken,
          converExtId,
          chatData,
          fetchDataType,
        });
      } else {
        console.warn("[chat2] non-ok", res.status);
      }
    } catch (error) {
      console.error("Unexpected tools error: " + error);
      alert("Unexpected tools error, please check console.");
    }
  };

  async function helperFetchCharacterInfo(fetchUrl, AccessToken, payload) {
    return fetch(fetchUrl, {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
        authorization: AccessToken,
      },
      body: JSON.stringify(payload),
    }).then(async (res) => {
      let data = await res.json().catch(() => ({}));
      if (!data.character || data.character.length === 0) {
        const newUrl = "https://plus.character.ai/chat/character/info/";
        if (fetchUrl !== newUrl) {
          try {
            console.log("Trying other character fetch method...");
            data = await helperFetchCharacterInfo(newUrl, AccessToken, payload);
          } catch {}
        }
      }
      return data;
    });
  }

  const fetchHistory = async () => {
    const AccessToken = getAccessToken();
    const charId = getCharId();
    if (!AccessToken || !charId) return;

    let meta = document.querySelector('meta[cai_charId="' + charId + '"]');
    if (!meta) {
      meta = document.createElement("meta");
      meta.setAttribute("cai_charId", charId);
      document.head.appendChild(meta);
    }
    if (meta.getAttribute("fetchHistStarted")) {
      if (meta.getAttribute("cai_history")) {
        handleProgressInfoHist(`(Data is ready!)`);
      }
      return;
    }
    meta.setAttribute("fetchHistStarted", "true");
    document
      .querySelector(".cai_tools-cont .fetchHistory-btn")
      .classList.add("started");

    let chatList = [];
    try {
      try {
        const res_legacy = await fetch(
          "https://plus.character.ai/chat/character/histories_v2/",
          {
            method: "POST",
            headers: {
              Accept: "application/json",
              "Content-Type": "application/json",
              authorization: AccessToken,
            },
            body: JSON.stringify({ external_id: charId, number: 999 }),
          }
        );
        if (res_legacy.ok) {
          const data = await res_legacy.json();
          if (data?.histories?.length) {
            const filtered = data.histories.filter(
              (chat) => (chat.msgs?.length ?? 0) > 1
            );
            chatList.push(
              ...filtered.map((chat) => ({
                id: chat.external_id,
                date: new Date(chat.created),
                type: "legacy",
              }))
            );
          }
        } else {
          console.log("[histories_v2] skipped:", res_legacy.status);
        }
      } catch (e) {
        console.log("[histories_v2] failed:", e);
      }

      const res_new = await fetch(
        `https://neo.character.ai/chats/?character_ids=${charId}&num_preview_turns=2`,
        {
          method: "GET",
          headers: {
            Accept: "application/json",
            "Content-Type": "application/json",
            authorization: AccessToken,
          },
        }
      );
      if (res_new.ok) {
        const data = await res_new.json();
        if (data?.chats?.length) {
          const filtered = data.chats.filter(
            (c) => (c.preview_turns?.length ?? 0) > 1
          );
          chatList.push(
            ...filtered.map((chat) => ({
              id: chat.chat_id,
              date: new Date(chat.create_time),
              type: "chat2",
            }))
          );
        }
      } else {
        console.warn("[neo/chats] non-ok:", res_new.status);
      }
    } catch (error) {
      console.log("fetchHistory error: " + error);
    }

    if (!chatList.length) {
      alert("Failed to get history");
      return;
    }

    chatList.sort((a, b) => b.date - a.date);

    let finalHistory = [];
    let fetchedChatNumber = 0;
    const historyLength = chatList?.length || 0;

    for (const chatInfo of chatList) {
      const { id, date, type } = chatInfo;
      const chatData = { history: [], turns: [] };

      try {
        if (type === "legacy") {
          await fetchMessagesLegacy({
            AccessToken,
            nextPage: 0,
            converExtId: id,
            chatData,
            fetchDataType: "history",
          });
        } else {
          await fetchMessagesChat2({
            AccessToken,
            nextToken: null,
            converExtId: id,
            chatData,
            fetchDataType: "history",
          });
        }
        finalHistory.push({ date, chat: chatData.history });
      } catch (e) {
        console.warn("[history] fetch failed for chat", id, e);
      }

      fetchedChatNumber++;
      handleProgressInfoHist(
        `(Loading history... ${fetchedChatNumber}/${historyLength})`
      );
    }

    meta.setAttribute("cai_history", JSON.stringify(finalHistory));
    handleProgressInfoHist(`(The data is ready!)`);
    console.log("FINISHED", finalHistory);
  };

  const fetchConversation = async (converExtId) => {
    const AccessToken = getAccessToken();
    if (!AccessToken) return;
    const chatData = { history: [], turns: [] };
    const args = {
      AccessToken,
      converExtId,
      chatData,
      fetchDataType: "conversation",
    };

    const location = getPageType();
    if (
      location === "character.ai/chat" ||
      location.includes(".character.ai/chat2")
    ) {
      args.nextToken = null;
      await fetchMessagesChat2(args);
    } else if (location.includes(".character.ai/chat") && getCharId()) {
      args.nextPage = 0;
      await fetchMessagesLegacy(args);
    }
  };

  // Tools - DOM

  function initialize_caitools() {
    const BODY = document.getElementsByTagName("BODY")[0];

    const cai_tools_string = `
      <div class="cait_button-cont" data-tool="cai_tools">
        <div class="dragCaitBtn">&#9946;</div>
        <button class="cai_tools-btn">Character.AI Study Tool</button>
      </div>
      <div class="cai_tools-cont" data-tool="cai_tools">
        <div class="cai_tools">
          <div class="cait-header">
            <h4>Character.AI Study Tool</h4><span class="cait-close">x</span>
          </div>
          <div class="cait-body">
            <div class="history_loading-cont">
              <button type="button" class="fetchHistory-btn">Request Data</button>
              <span class='cait_progressInfo_Hist'>(Click the button to request data)</span>
            </div>
            <ul>
              <li data-cait_type='cai_hist_offline_read'>Select History</li>
            </ul>
          </div>
        </div>
      </div>
      <div class="cait_info-cont" data-tool="cai_tools">
        <div class="cait_info">
          <div class="caiti_header">
            <h4>Character.AI Tool</h4><span class="caiti-close">x</span>
          </div>
          <div class="caiti-body"></div>
        </div>
      </div>
    `;
    BODY.appendChild(parseHTML_caiTools(cai_tools_string));

    document
      .querySelector(".cai_tools-btn")
      .addEventListener("mouseup", openModal);
    document
      .querySelector(".cai_tools-btn")
      .addEventListener("touchstart", openModal);
    async function openModal() {
      const AccessToken = getAccessToken();
      if (!AccessToken) {
        alert("Access Token is not ready yet.");
        return;
      }
      document.querySelector(".cai_tools-cont").classList.add("active");

      let currentConverExtId = await getCurrentConverId();
      const checkExistingConver = document.querySelector(
        `meta[cai_converExtId="${currentConverExtId}"]`
      );
      if (checkExistingConver?.getAttribute("cai_conversation") != null) {
        handleProgressInfo("(Ready!)");
        return;
      } else if (!checkExistingConver?.getAttribute("cai_fetchStarted")) {
        const meta =
          checkExistingConver ||
          (() => {
            const m = document.createElement("meta");
            m.setAttribute("cai_converExtId", currentConverExtId);
            document.head.appendChild(m);
            return m;
          })();
        meta.setAttribute("cai_fetchStarted", "true");
        fetchConversation(currentConverExtId);
      }
    }

    document
      .querySelector(".cai_tools-cont")
      .addEventListener("click", (event) => {
        const target = event.target;
        if (
          target.classList.contains("cai_tools-cont") ||
          target.classList.contains("cait-close")
        ) {
          close_caiToolsModal();
        }
      });

    document
      .querySelector(".cai_tools-cont .fetchHistory-btn")
      .addEventListener("click", () => fetchHistory());

    document
      .querySelector('.cai_tools-cont [data-cait_type="cai_hist_offline_read"]')
      .addEventListener("click", () => {
        const args = { downloadType: "cai_hist_offline_read" };
        DownloadHistory(args);
        close_caiToolsModal();
      });
  }

  function close_caiToolsModal() {
    document.querySelector(".cai_tools-cont").classList.remove("active");
  }
  function close_caitSettingsModal() {
    document.querySelector(".cait_settings-cont")?.classList.remove("active");
  }
  function close_caitMemoryManagerModal() {
    document
      .querySelector(".cait_memory_manager-cont")
      ?.classList.remove("active");
  }
  function close_caitInfoModal() {
    document.querySelector(".cait_info-cont")?.classList.remove("active");
  }

  function MemoryManager() {
    try {
      const container = document.querySelector(".cait_memory_manager-cont");
      const mmActive = container.querySelector('input[name="cait_mm_active"]');
      const remindFrequency = container.querySelector(
        'input[name="remind_frequency"]'
      );
      const newMemoryField = container.querySelector(".mm_new_memory");
      const addNewMemoryBtn = container.querySelector(".add_new_memory");
      const currentMemoryList = container.querySelector(
        ".mm-current_memory_list"
      );
      const cancelPlan = container.querySelector(".cancel");
      const savePlan = container.querySelector(".save");

      const pushToMemoryList = (memory) => {
        const li = document.createElement("li");
        const textarea = document.createElement("textarea");
        textarea.classList.add("memory");
        textarea.value = memory;
        const deleteBtn = document.createElement("button");
        deleteBtn.type = "button";
        deleteBtn.classList.add("delete_memory");
        deleteBtn.textContent = "Delete";
        deleteBtn.addEventListener("click", () => li.remove());
        li.appendChild(textarea);
        li.appendChild(deleteBtn);
        currentMemoryList.appendChild(li);
      };

      const defaultSettings = {
        mmActive: false,
        mmRemindFrequency: 5,
        mmList: [],
      };

      let caiToolsSettings = JSON.parse(localStorage.getItem("cai_tools"));
      if (!caiToolsSettings) {
        caiToolsSettings = { memoryManager: defaultSettings };
      } else if (!caiToolsSettings.memoryManager) {
        caiToolsSettings.memoryManager = defaultSettings;
      }
      const settings = caiToolsSettings.memoryManager;

      if (container.dataset.import_needed === "true") {
        mmActive.checked = settings.mmActive;
        remindFrequency.value =
          settings.mmRemindFrequency >= 0 ? settings.mmRemindFrequency : 5;
        if (!settings.mmList) settings.mmList = [];
        const charId = getCharId();
        if (!charId) throw "Char ID is undefined";
        const charSettings = settings.mmList.find((obj) => obj.char === charId);
        if (charSettings) {
          currentMemoryList.innerHTML = "";
          charSettings.list.forEach(pushToMemoryList);
        } else {
          settings.mmList.push({ char: charId, timesSkipped: 0, list: [] });
        }
        container.dataset.import_needed = "false";
      }

      addNewMemoryBtn.addEventListener("click", () => {
        if (newMemoryField.value.trim().length === 0) return;
        pushToMemoryList(newMemoryField.value.trim());
        newMemoryField.value = "";
      });

      cancelPlan.addEventListener("click", () => {
        container.dataset.import_needed = "true";
        close_caitMemoryManagerModal();
      });

      savePlan.addEventListener("click", () => {
        try {
          settings.mmActive = mmActive.checked;
          settings.mmRemindFrequency =
            +remindFrequency.value >= 0 && +remindFrequency.value < 100
              ? +remindFrequency.value
              : 5;
          const charId = getCharId();
          if (!charId) throw "Char ID is undefined";
          const charSettings = settings.mmList.find(
            (obj) => obj.char === charId
          );
          charSettings.list = [];
          [...currentMemoryList.children].forEach((li) => {
            const memory = li.querySelector("textarea").value.trim();
            if (memory.length > 0) {
              charSettings.list.push(memory);
            }
          });
          localStorage.setItem("cai_tools", JSON.stringify(caiToolsSettings));
          close_caitMemoryManagerModal();
        } catch (error) {
          console.log("Screenshot this error please; ", error);
          alert(
            "Couldn't be saved. Check console for details (F12 → Console) and report."
          );
        }
      });

      container.classList.add("active");
    } catch (error) {
      console.log("Screenshot this error please; ", error);
      alert(
        "Memory manager couldn't be opened. Please create an issue with the console error (F12 → Console)."
      );
    }
  }

  async function DownloadConversation(args) {
    const currentConversation = await getCurrentConverId();
    if (!currentConversation) {
      alert("Current conversation ID couldn't be found.");
      return;
    }
    const chatData = JSON.parse(
      document
        .querySelector(`meta[cai_converExtId="${currentConversation}"]`)
        ?.getAttribute("cai_conversation") || "null"
    );
    if (chatData == null) {
      alert("Data doesn't exist or not ready. Try again later.");
      return;
    }

    const charName = chatData[0]?.name ?? "NULL!";
    console.log("chatData: ", chatData);

    switch (args.downloadType) {
      case "cai_offline_read":
        Download_OfflineReading(chatData);
        break;
      default:
        break;
    }
  }

  async function DuplicateChat(chatData, maxMsgLength) {
    try {
      if (maxMsgLength) chatData = chatData.slice(-maxMsgLength);

      const charId = getCharId();
      const userInfo = await getUserId({ withUsername: true });
      if (!userInfo || !charId) {
        alert("Requirements missing, can't proceed to duplication.");
        return;
      }
      const { userId, username } = userInfo;

      let caiToolsSettings = JSON.parse(localStorage.getItem("cai_tools"));
      if (caiToolsSettings && caiToolsSettings.memoryManager) {
        caiToolsSettings.memoryManager.mmActive = false;
        localStorage.setItem("cai_tools", JSON.stringify(caiToolsSettings));
      }

      const socket = new WebSocket("wss://neo.character.ai/ws/");
      let msgIndex = 0;
      let prevThisTurnId = "";
      const randomOriginId = crypto.randomUUID();
      let chatIdNew = "";
      let abortedReqs = [];

      const infoContainer = document.querySelector(".cait_info-cont");
      const infoBody = infoContainer.querySelector(".caiti-body");
      infoBody.innerHTML = "Creating new chat...";
      infoContainer.classList.add("active");
      let chatIsCreated = false;

      const sendCreateChatMessage = () => {
        const createChatPayload = {
          command: "create_chat",
          request_id: crypto.randomUUID(),
          payload: {
            chat: {
              chat_id: crypto.randomUUID(),
              creator_id: userId.toString(),
              visibility: "VISIBILITY_PRIVATE",
              character_id: charId,
              type: "TYPE_ONE_ON_ONE",
            },
            with_greeting: true,
          },
          origin_id: randomOriginId,
        };
        socket.send(JSON.stringify(createChatPayload));
      };
      if (socket.readyState === 1) sendCreateChatMessage();
      else if (socket.readyState === 0)
        socket.addEventListener("open", sendCreateChatMessage);
      else throw "Socket readyState: " + socket.readyState;

      socket.addEventListener("close", (event) => {
        if (!chatIsCreated) {
          alert("Error when trying to create new chat.");
          console.log(" Tools error: " + event);
        }
      });

      socket.addEventListener("message", (event) => {
        if (!event.data) return;
        const wsdata = JSON.parse(event.data);

        if (wsdata.command === "create_chat_response") {
          if (
            !wsdata.chat ||
            !wsdata.chat.character_id ||
            !wsdata.chat.chat_id
          ) {
            alert(
              "New chat requirements missing, can't proceed to duplication."
            );
            return;
          }
          chatIdNew = wsdata.chat.chat_id;
          const newChatPage = `https://${getMembership()}.character.ai/chat2?char=${charId}&hist=${chatIdNew}`;
          const newChatPage_Redesign = `https://character.ai/chat/${charId}?hist=${chatIdNew}`;
          console.log(newChatPage, newChatPage_Redesign);
          chatIsCreated = true;
        } else if (wsdata.command === "remove_turns_response") {
          const msg = chatData[msgIndex];
          const thisTurnId = crypto.randomUUID();
          msgIndex++;
          infoBody.innerHTML = `<p>Recreating messages from scratch ${msgIndex}/${chatData.length}</p>`;
          const sendUserMessageAgainPayload = {
            command: "create_and_generate_turn",
            request_id: crypto.randomUUID(),
            payload: {
              num_candidates: 1,
              tts_enabled: false,
              selected_language: "English",
              character_id: charId,
              user_name: username,
              turn: {
                turn_key: { turn_id: thisTurnId, chat_id: chatIdNew },
                author: {
                  author_id: userId.toString(),
                  is_human: true,
                  name: username,
                },
                candidates: [
                  { candidate_id: thisTurnId, raw_content: msg.message },
                ],
                primary_candidate_id: thisTurnId,
              },
              previous_annotations: {
                boring: 0,
                not_boring: 0,
                inaccurate: 0,
                not_inaccurate: 0,
                repetitive: 0,
                not_repetitive: 0,
                out_of_character: 0,
                not_out_of_character: 0,
                bad_memory: 0,
                not_bad_memory: 0,
                long: 0,
                not_long: 0,
                short: 0,
                not_short: 0,
                ends_chat_early: 0,
                not_ends_chat_early: 0,
                funny: 0,
                not_funny: 0,
                interesting: 0,
                not_interesting: 0,
                helpful: 0,
                not_helpful: 0,
              },
              update_primary_candidate: {
                candidate_id: prevThisTurnId,
                turn_key: { turn_id: prevThisTurnId, chat_id: chatIdNew },
              },
            },
            origin_id: randomOriginId,
          };
          socket.send(JSON.stringify(sendUserMessageAgainPayload));
        } else if (
          wsdata.command === "add_turn" ||
          wsdata.command === "update_turn"
        ) {
          if (!wsdata.turn.candidates[0].is_final) return;
          else if (wsdata.turn.author.is_human) return;
          else if (msgIndex >= chatData.length) {
            const infoBody = document.querySelector(
              ".cait_info-cont .caiti-body"
            );
            const newChatPage = `https://${getMembership()}.character.ai/chat2?char=${charId}&hist=${chatIdNew}`;
            const newChatPage_Redesign = `https://character.ai/chat/${charId}?hist=${chatIdNew}`;
            infoBody.innerHTML = `
              <p>
                Complete! Duplicate chat;
                <br /><br />
                <a href="${newChatPage}" target="_blank">Old design chat link</a>
                <br /><br />
                <a href="${newChatPage_Redesign}" target="_blank">Redesign chat link</a>
              </p>`;
            return;
          }

          const msg = chatData[msgIndex];
          const prevMsgWasHuman = chatData[msgIndex - 1]
            ? chatData[msgIndex - 1].isHuman
            : false;

          const thisTurnId = crypto.randomUUID();
          prevThisTurnId = thisTurnId;
          const turnKey = wsdata.turn.turn_key.turn_id;
          const candidateId = wsdata.turn.primary_candidate_id;
          msgIndex++;

          const infoBody2 = document.querySelector(
            ".cait_info-cont .caiti-body"
          );
          if (infoBody2) {
            infoBody2.innerHTML = `<p>Recreating messages from scratch ${msgIndex}/${chatData.length}</p>`;
          }

          if (msg.isHuman && !prevMsgWasHuman) {
            const sendUserMessagePayload = {
              command: "create_and_generate_turn",
              request_id: crypto.randomUUID(),
              payload: {
                num_candidates: 1,
                tts_enabled: false,
                selected_language: "English",
                character_id: charId,
                user_name: username,
                turn: {
                  turn_key: { turn_id: thisTurnId, chat_id: chatIdNew },
                  author: {
                    author_id: userId.toString(),
                    is_human: true,
                    name: username,
                  },
                  candidates: [
                    { candidate_id: thisTurnId, raw_content: msg.message },
                  ],
                  primary_candidate_id: thisTurnId,
                },
                previous_annotations: {
                  boring: 0,
                  not_boring: 0,
                  inaccurate: 0,
                  not_inaccurate: 0,
                  repetitive: 0,
                  not_repetitive: 0,
                  out_of_character: 0,
                  not_out_of_character: 0,
                  bad_memory: 0,
                  not_bad_memory: 0,
                  long: 0,
                  not_long: 0,
                  short: 0,
                  not_short: 0,
                  ends_chat_early: 0,
                  not_ends_chat_early: 0,
                  funny: 0,
                  not_funny: 0,
                  interesting: 0,
                  not_interesting: 0,
                  helpful: 0,
                  not_helpful: 0,
                },
                update_primary_candidate: {
                  candidate_id: candidateId,
                  turn_key: { turn_id: turnKey, chat_id: chatIdNew },
                },
              },
              origin_id: randomOriginId,
            };
            socket.send(JSON.stringify(sendUserMessagePayload));
          } else if (msg.isHuman && prevMsgWasHuman) {
            const deleteCharMessagePayload = {
              command: "remove_turns",
              request_id: crypto.randomUUID(),
              payload: {
                chat_id: wsdata.turn.turn_key.chat_id,
                turn_ids: [turnKey],
              },
              origin_id: randomOriginId,
            };
            socket.send(JSON.stringify(deleteCharMessagePayload));
          } else {
            const editCharMessagePayload = {
              command: "edit_turn_candidate",
              request_id: crypto.randomUUID(),
              payload: {
                turn_key: {
                  chat_id: wsdata.turn.turn_key.chat_id,
                  turn_id: turnKey,
                },
                current_candidate_id: wsdata.turn.candidates[0].candidate_id,
                new_candidate_raw_content: msg.message,
              },
              origin_id: randomOriginId,
            };
            socket.send(JSON.stringify(editCharMessagePayload));
          }
        } else {
          console.log("WS Data:", wsdata);
        }
      });
    } catch (error) {
      console.log(error);
    }
  }

  function DownloadConversation_Oobabooga(chatData, charName) {
    const ChatObject = {
      internal: [],
      visible: [],
      data: [],
      data_visible: [],
    };

    let currentPair = [];
    let prevName = null;

    // User's message first
    chatData.shift();

    chatData.forEach((msg) => {
      if (msg.name === prevName) {
        const dataLength = ChatObject.internal.length - 1;
        const pairLength = ChatObject.internal[dataLength].length - 1;
        let mergedMessage = (ChatObject.internal[dataLength][pairLength] +=
          "\n\n" + msg.message);
        ChatObject.visible[dataLength][pairLength] = mergedMessage;
        ChatObject.data[dataLength][pairLength] = mergedMessage;
        ChatObject.data_visible[dataLength][pairLength] = mergedMessage;
        return;
      }

      currentPair.push(msg.message);
      if (currentPair.length === 2) {
        ChatObject.internal.push(currentPair);
        ChatObject.visible.push(currentPair);
        ChatObject.data.push(currentPair);
        ChatObject.data_visible.push(currentPair);
        currentPair = [];
      }
      prevName = msg.name;
    });

    const Data_FinalForm = JSON.stringify(ChatObject);
    const blob = new Blob([Data_FinalForm], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${charName}_oobabooga_Chat.json`;
    link.click();
  }

  function DownloadConversation_Tavern(chatData, charName) {
    const blob = CreateTavernChatBlob(chatData, charName);
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${charName}_tavern_Chat.jsonl`;
    link.click();
  }

  function DownloadConversation_ChatExample(chatData, charName) {
    const messageList = [];
    messageList.push("<START>");
    chatData.forEach((msg) => {
      const messager = msg.name == charName ? "char" : "user";
      const message = `{{${messager}}}: ${msg.message}`;
      messageList.push(message);
    });

    const definitionString = messageList.join("\n");
    const blob = new Blob([definitionString], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${charName}_Example.txt`;
    link.click();
  }

  function CreateTavernChatBlob(chatData, charName) {
    const userName = "You";
    const createDate = Date.now();
    const initialPart = JSON.stringify({
      user_name: userName,
      character_name: charName,
      create_date: createDate,
    });
    const outputLines = [initialPart];

    let prevName = null;
    chatData.forEach((msg) => {
      if (msg.name === prevName) {
        let mergedMessage = JSON.parse(outputLines[outputLines.length - 1]);
        mergedMessage.mes += "\n\n" + msg.message;
        outputLines[outputLines.length - 1] = JSON.stringify(mergedMessage);
        return;
      }

      const formattedMessage = JSON.stringify({
        name: msg.name !== charName ? "You" : charName,
        is_user: msg.name !== charName,
        is_name: true,
        send_date: Date.now(),
        mes: msg.message,
      });

      outputLines.push(formattedMessage);
      prevName = msg.name;
    });

    const outputString = outputLines.join("\n");
    return new Blob([outputString], { type: "application/jsonl" });
  }

  function DownloadHistory(args) {
    const charId = getCharId();
    const historyData = JSON.parse(
      document
        .querySelector('meta[cai_charId="' + charId + '"]')
        ?.getAttribute("cai_history") || "null"
    );

    if (historyData == null) {
      alert("Data doesn't exist or not ready. Try again later.");
      return;
    }

    switch (args.downloadType) {
      case "cai_hist_offline_read":
        Download_OfflineReading(historyData);
        break;
      default:
        break;
    }
  }

  async function Download_OfflineReading(data) {
    let default_character_name =
      data?.[0]?.name ??
      data?.[data.length - 1]?.chat?.[0]?.name ??
      data?.[0]?.chat?.[0]?.name ??
      "Chat";

    const AccessToken = getAccessToken();
    const charId = getCharId();
    let charResolved = {
      name: null,
      avatar_file_name: null,
      description: null,
      greeting: null,
      raw: {},
    };
    if (charId) {
      try {
        charResolved = await resolveCharacterData(charId, AccessToken);
      } catch (e) {
        console.warn("[cai-tools] character resolver failed:", e);
      }
    }

    let charPicture = null;
    if (charResolved.avatar_file_name) {
      charPicture = `https://characterai.io/i/80/static/avatars/${charResolved.avatar_file_name}`;
    } else {
      charPicture = await getAvatar("80", "char").catch(() => null);
    }
    const userPicture = await getAvatar("80", "user").catch(() => null);

    let offlineHistory = [];
    if (Array.isArray(data?.[0]?.chat)) {
      data.forEach((chat) => {
        const chatTemp = [];
        (chat.chat || []).forEach((msg) =>
          chatTemp.push({
            isUser: msg.isHuman,
            name: msg.name,
            message: encodeURIComponent(msg.message || ""),
          })
        );
        offlineHistory.push({ date: chat.date, chat: chatTemp });
      });
    } else {
      const chatTemp = [];
      (data || []).forEach((msg) =>
        chatTemp.push({
          isUser: msg.isHuman,
          name: msg.name,
          message: encodeURIComponent(msg.message || ""),
        })
      );
      offlineHistory.push({
        date: data?.[0]?.date ?? new Date(),
        chat: chatTemp,
      });
    }

    function escapeJsonString(str) {
      return str
        .replace(/\\/g, "\\\\")
        .replace(/"/g, '\\"')
        .replace(/\n/g, "\\n")
        .replace(/\r/g, "\\r")
        .replace(/\t/g, "\\t");
    }

    const finalData = {
      charPic: charPicture,
      userPic: userPicture,
      charData: charResolved.raw || {},
      charName: (charResolved.name ?? default_character_name) || "Chat",
      history: offlineHistory,
    };
    console.log("[offline] charData:", finalData.charData);

    const fileUrl = extAPI.runtime.getURL("ReadOffline.html");
    const xhr = new XMLHttpRequest();
    xhr.open("GET", fileUrl, true);
    xhr.onreadystatechange = function () {
      if (xhr.readyState === 4) {
        if (xhr.status !== 200) {
          alert("Failed to load offline reader template.");
          return;
        }
        let fileContents = xhr.responseText;

        fileContents = fileContents.replace(
          /<<<REPLACE_THIS_TEXT>>>/g,
          escapeJsonString(JSON.stringify(finalData))
        );

        const selectImageUrl = extAPI.runtime.getURL("../img/select.png");
        const selectedImageUrl = extAPI.runtime.getURL("../img/selected.png");
        fileContents = fileContents.replace(
          /img\/select\.png/g,
          selectImageUrl
        );
        fileContents = fileContents.replace(
          /img\/selected\.png/g,
          selectedImageUrl
        );

        const blob = new Blob([fileContents], { type: "text/html" });
        const url = URL.createObjectURL(blob);

        let newWindow = null;
        try {
          newWindow = window.open();
        } catch {}
        if (!newWindow) {
          const html = `
            <html><head><meta charset="utf-8"><title>Offline Chat</title></head>
            <body style="margin:0">
              <iframe src="${url}" frameborder="0" style="border:none;width:100%;height:100vh"></iframe>
            </body></html>`;
          const blob2 = new Blob([html], { type: "text/html" });
          const url2 = URL.createObjectURL(blob2);
          location.assign(url2);
          return;
        }

        newWindow.document.open();
        newWindow.document.write(`
          <html>
            <head><title>Offline Chat</title></head>
            <body style="margin:0;">
              <iframe src="${url}" frameborder="0" style="border:none; width:100%; height:100%;"></iframe>
            </body>
          </html>
        `);
        newWindow.document.close();
      }
    };
    xhr.send();
  }

  function DownloadCharacter(args) {
    const fetchUrl = "https://plus.character.ai/chat/character/";
    const AccessToken = getAccessToken();
    const charId = getCharId();
    const payload = { external_id: charId };
    if (AccessToken != null && charId != null) {
      fetchCharacterInfo(fetchUrl, AccessToken, payload, args.downloadType);
    } else {
      alert("Couldn't find logged in user or character id.");
    }
  }

  function fetchCharacterInfo(fetchUrl, AccessToken, payload, downloadType) {
    fetch(fetchUrl, {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
        authorization: AccessToken,
      },
      body: JSON.stringify(payload),
    })
      .then((res) => (res.ok ? res.json() : Promise.reject(res)))
      .then((data) => {
        if (!data.character || data.character.length === 0) {
          const newUrl = "https://plus.character.ai/chat/character/info/";
          if (fetchUrl != newUrl) {
            fetchCharacterInfo(newUrl, AccessToken, payload, downloadType);
          } else {
            alert(
              "Character settings are not available (likely restricted to paid accounts)."
            );
          }
          return;
        }

        let {
          name,
          title,
          description,
          greeting,
          avatar_file_name,
          definition,
          categories,
        } = data.character;

        if (downloadType === "cai_character_hybrid") {
          const hybridCharacter = {
            char_name: name,
            char_persona: description,
            char_greeting: greeting,
            world_scenario: "",
            example_dialogue: definition ?? "",
            name: name,
            description: description,
            first_mes: greeting,
            scenario: "",
            mes_example: definition ?? "",
            personality: title,
            metadata: metadata,
          };

          const Data_FinalForm = JSON.stringify(hybridCharacter);
          const blob = new Blob([Data_FinalForm], { type: "application/json" });
          const downloadUrl = URL.createObjectURL(blob);
          const link = document.createElement("a");
          link.href = downloadUrl;
          link.download = name.replaceAll(" ", "_") + ".json";
          link.click();
        } else if (downloadType === "cai_character_card") {
          if (!avatar_file_name) {
            alert("Only works on characters who have an avatar.");
            return;
          }

          const cardCharacter = {
            name,
            description,
            first_mes: greeting,
            scenario: "",
            mes_example: definition ?? "",
            personality: title,
            metadata: metadata,
          };

          const avatarLink = `https://characterai.io/i/400/static/avatars/${avatar_file_name}`;
          const charInfo = JSON.stringify(cardCharacter, undefined, "\t");

          fetch(avatarLink)
            .then((res) => res.blob())
            .then((avifBlob) => {
              const img = new Image();
              const objectURL = URL.createObjectURL(avifBlob);
              img.src = objectURL;

              img.onload = function () {
                const canvas = document.createElement("canvas");
                canvas.width = img.width;
                canvas.height = img.height;
                const ctx = canvas.getContext("2d");
                ctx.drawImage(img, 0, 0);
                canvas.toBlob((canvasBlob) => {
                  const fileReader = new FileReader();
                  fileReader.onload = function (event) {
                    const chunks = extractChunks(
                      new Uint8Array(event.target.result)
                    ).filter((x) => x.name !== "tEXt");

                    const keyword = [99, 104, 97, 114, 97]; // "chara"
                    const encodedValue = btoa(
                      new TextEncoder()
                        .encode(charInfo)
                        .reduce((a, b) => a + String.fromCharCode(b), "")
                    );
                    const valueBytes = [];
                    for (let i = 0; i < encodedValue.length; i++) {
                      valueBytes.push(encodedValue.charCodeAt(i));
                    }
                    const tEXtChunk = {
                      name: "tEXt",
                      data: new Uint8Array([...keyword, 0, ...valueBytes]),
                    };

                    const iendIndex = chunks.findIndex(
                      (obj) => obj.name === "IEND"
                    );
                    chunks.splice(iendIndex, 0, tEXtChunk);

                    const combinedData = [];
                    combinedData.push(...[137, 80, 78, 71, 13, 10, 26, 10]);
                    chunks.forEach((chunk) => {
                      const length = chunk.data.length;
                      const lengthBytes = new Uint8Array(4);
                      lengthBytes[0] = (length >> 24) & 0xff;
                      lengthBytes[1] = (length >> 16) & 0xff;
                      lengthBytes[2] = (length >> 8) & 0xff;
                      lengthBytes[3] = length & 0xff;

                      const type = chunk.name
                        .split("")
                        .map((char) => char.charCodeAt(0));

                      const crc = CRC32.buf(chunk.data, CRC32.str(chunk.name));

                      const crcBytes = new Uint8Array(4);
                      crcBytes[0] = (crc >> 24) & 0xff;
                      crcBytes[1] = (crc >> 16) & 0xff;
                      crcBytes[2] = (crc >> 8) & 0xff;
                      crcBytes[3] = crc & 0xff;

                      combinedData.push(
                        ...lengthBytes,
                        ...type,
                        ...chunk.data,
                        ...crcBytes
                      );
                    });

                    const newDataBlob = new Blob(
                      [new Uint8Array(combinedData).buffer],
                      { type: "image/png" }
                    );
                    const link = document.createElement("a");
                    link.href = URL.createObjectURL(newDataBlob);
                    link.download = name ?? "character_card.png";
                    link.click();
                  };
                  fileReader.readAsArrayBuffer(canvasBlob);
                }, "image/png");
              };
            })
            .catch(() => {
              console.error("Error while fetching avatar.");
            });
        } else if (downloadType === "cai_character_settings") {
          const avatarLink = avatar_file_name
            ? `https://characterai.io/i/400/static/avatars/${avatar_file_name}`
            : null;

          const settingsContent = `
            <span class="caits_field_name">Name</span>
            <p>${name}</p>
            <span class="caits_field_name">Short Description</span>
            <p>${title}</p>
            <span class="caits_field_name">Long Description</span>
            <p>${description.trim().length === 0 ? "(Empty)" : description}</p>
            <span class="caits_field_name">Greeting</span>
            <p>${parseMessageText(greeting)}</p>
            <span class="caits_field_name">Avatar Link</span>
            <p>${
              avatarLink
                ? `<a href="${avatarLink}" target="_blank">${avatarLink}</a>`
                : "(No avatar)"
            }</p>
            <span class="caits_field_name">Definition</span>
            <p>${
              definition == null
                ? "(Definition is private)"
                : definition.trim().length === 0
                ? "(Empty)"
                : parseMessageText(definition)
            }</p>
          `;

          const settingsContainer = document.querySelector(
            ".cait_settings .caits-content"
          );
          if (!settingsContainer) return;
          settingsContainer.innerHTML = settingsContent;
          settingsContainer
            .closest(".cait_settings-cont")
            .classList.add("active");
        } else if (downloadType === "character_copy") {
          const payload2 = {
            title: title,
            name: name,
            identifier: "id:" + crypto.randomUUID(),
            categories: categories ? categories.map((c) => c.name) : [],
            visibility: "PRIVATE",
            copyable: false,
            description: description,
            greeting: greeting,
            definition: definition ?? "",
            avatar_rel_path: avatar_file_name,
            img_gen_enabled: false,
            base_img_prompt: "",
            strip_img_prompt_from_msg: false,
            voice_id: "",
            default_voice_id: "",
          };
          fetch("https://plus.character.ai/chat/character/create/", {
            method: "POST",
            headers: {
              Accept: "application/json",
              "Content-Type": "application/json",
              authorization: AccessToken,
            },
            body: JSON.stringify(payload2),
          })
            .then((res) => (res.ok ? res.json() : Promise.reject(res)))
            .then((data) => {
              if (!data.character || !data.character.external_id) return;
              const infoContainer = document.querySelector(".cait_info-cont");
              const infoBody = infoContainer.querySelector(".caiti-body");
              infoBody.innerHTML = `
                <p>
                  Your private character;
                  <br /><br />
                  <a href="https://beta.character.ai/chat2?char=${data.character.external_id}" target="_blank">Old design link</a>
                  <br /><br />
                  <a href="https://character.ai/chat/${data.character.external_id}" target="_blank">Redesign link</a>
                </p>`;
              infoContainer.classList.add("active");
            })
            .catch(() =>
              alert(
                "Character copy failed. This action may be restricted for non-paid accounts."
              )
            );
        }
      })
      .catch(() =>
        alert("Character info is not accessible (likely paywalled).")
      );
  }

  // UTILITY

  async function getUserId(settings = { withUsername: false }) {
    const AccessToken = getAccessToken();
    if (!AccessToken) return null;
    return await fetch(`https://plus.character.ai/chat/user/`, {
      method: "GET",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
        authorization: AccessToken,
      },
    })
      .then((res) => (res.ok ? res.json() : Promise.reject(res)))
      .then((data) => {
        if (!data?.user?.user?.id) {
          return null;
        }
        if (settings.withUsername) {
          return {
            userId: data.user.user.id,
            username: data.user.user.account.name,
          };
        } else {
          return { userId: data.user.user.id };
        }
      })
      .catch((err) => {
        console.log("Error while fetching user Id;", err);
        return null;
      });
  }

  async function getAvatar(avatarSize, identity) {
    try {
      const AccessToken = getAccessToken();
      if (identity === "char") {
        const charId = getCharId();
        const resolved = await resolveCharacterData(charId, AccessToken);
        if (resolved.avatar_file_name) {
          return `https://characterai.io/i/${avatarSize}/static/avatars/${resolved.avatar_file_name}`;
        }
        return null;
      } else {
        if (!AccessToken) return null;
        const res = await fetch(`https://plus.character.ai/chat/user/`, {
          method: "GET",
          headers: {
            Accept: "application/json",
            "Content-Type": "application/json",
            authorization: AccessToken,
          },
        });
        if (!res.ok) return null;
        const data = await res.json();
        const avatarPath = data?.user?.user?.account?.avatar_file_name ?? null;
        if (!avatarPath) return null;

        const avatarLink = `https://characterai.io/i/${avatarSize}/static/avatars/${avatarPath}`;
        const avatarResponse = await fetch(avatarLink);
        if (!avatarResponse.ok) return null;
        const blob = await avatarResponse.blob();
        const reader = new FileReader();
        return await new Promise((resolve) => {
          reader.onload = () => resolve(reader.result);
          reader.onerror = () => resolve(null);
          reader.readAsDataURL(blob);
        });
      }
    } catch {
      return null;
    }
  }

  function getCharId() {
    const location = getPageType();
    if (location === "character.ai/chat") {
      return window.location.pathname.split("/")[2];
    } else {
      try {
        const url = new URL(window.location.href);
        const searchParams = new URLSearchParams(url.search);
        return searchParams.get("char");
      } catch {
        return null;
      }
    }
  }

  function getPageType() {
    return (
      window.location.hostname + "/" + window.location.pathname.split("/")[1]
    );
  }

  function getProgressInfo() {
    return document.querySelector(".cai_tools-cont .cait_progressInfo")
      ?.textContent;
  }

  function checkPlus() {
    return window.location.hostname.indexOf("plus") > -1 ? true : false;
  }

  function getMembership() {
    return window.location.hostname.indexOf("plus") > -1 ? "plus" : "beta";
  }

  function getAccessToken() {
    const meta = document.querySelector("meta[cai_token]");
    let token = meta ? meta.getAttribute("cai_token") : null;

    if (!token) {
      try {
        token =
          localStorage.getItem("char_token") ||
          sessionStorage.getItem("char_token");
      } catch {}
    }
    if (!token) return null;
    return token.startsWith("Token ") ? token : `Token ${token}`;
  }

  async function getCurrentConverId() {
    try {
      const AccessToken = getAccessToken();
      const charId = getCharId();
      if (!AccessToken || !charId) return null;

      const url = new URL(window.location.href);
      const searchParams = new URLSearchParams(url.search);
      const location = getPageType();

      const historyId = searchParams.get("hist");
      if (historyId) return historyId;
      else if (
        location === "character.ai/chat" ||
        location.includes(".character.ai/chat2")
      ) {
        const res = await fetch(
          `https://neo.character.ai/chats/recent/${charId}`,
          {
            method: "GET",
            headers: { authorization: AccessToken },
          }
        );
        if (res.ok) {
          const data = await res.json();
          return data?.chats?.[0]?.chat_id ?? null;
        }
      } else {
        const res = await fetch(
          `https://plus.character.ai/chat/history/continue/`,
          {
            method: "POST",
            headers: {
              authorization: AccessToken,
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              character_external_id: charId,
              history_external_id: null,
            }),
          }
        );
        if (res.ok) {
          const data = await res.json();
          return data?.external_id ?? null;
        }
      }
    } catch (error) {
      console.error(error);
      return null;
    }
  }

  function parseHTML_caiTools(html) {
    const template = document.createElement("template");
    template.innerHTML = html;
    const content = template.content;

    makeDraggable(content.querySelector(".cait_button-cont"));

    const handleTapToDisable = (() => {
      let tapCount = 0;
      let tapTimer;
      function resetTapCount() {
        tapCount = 0;
      }
      return function () {
        tapCount++;
        if (tapCount === 1) {
          tapTimer = setTimeout(resetTapCount, 700);
        } else if (tapCount === 3) {
          cleanDOM();
          clearTimeout(tapTimer);
        }
      };
    })();
    content
      .querySelector(".dragCaitBtn")
      .addEventListener("mouseup", handleTapToDisable);
    content
      .querySelector(".dragCaitBtn")
      .addEventListener("touchstart", handleTapToDisable);

    return content;
  }

  function parseMessageText(message) {
    message = message.replace(
      /\*\*\*([\s\S]*?)\*\*\*/g,
      '<span class="bold-italic">$1</span>'
    );
    message = message.replace(
      /\*\*([\s\S]*?)\*\*/g,
      '<span class="bold">$1</span>'
    );
    message = message.replace(
      /\*([\s\S]*?)\*/g,
      '<span class="italic">$1</span>'
    );
    message = message.replace(/\n/g, "<br>");
    return message;
  }

  function makeDraggable(elmnt) {
    var pos1 = 0,
      pos2 = 0,
      pos3 = 0,
      pos4 = 0;
    const dragHandle = document.querySelector(".dragCaitBtn");
    if (dragHandle) {
      dragHandle.addEventListener("mousedown", dragMouseDown);
      dragHandle.addEventListener("touchstart", dragMouseDown);
    } else {
      elmnt.addEventListener("mousedown", dragMouseDown);
      elmnt.addEventListener("touchstart", dragMouseDown);
    }

    function dragMouseDown(e) {
      e = e || window.event;
      e.preventDefault();
      pos3 = e.type === "touchstart" ? e.touches[0].clientX : e.clientX;
      pos4 = e.type === "touchstart" ? e.touches[0].clientY : e.clientY;
      document.addEventListener("mouseup", closeDragElement);
      document.addEventListener("touchend", closeDragElement);
      document.addEventListener("mousemove", elementDrag);
      document.addEventListener("touchmove", elementDrag);
    }

    function elementDrag(e) {
      e = e || window.event;
      e.preventDefault();
      pos1 = pos3 - (e.type === "touchmove" ? e.touches[0].clientX : e.clientX);
      pos2 = pos4 - (e.type === "touchmove" ? e.touches[0].clientY : e.clientY);
      pos3 = e.type === "touchmove" ? e.touches[0].clientX : e.clientX;
      pos4 = e.type === "touchmove" ? e.touches[0].clientY : e.clientY;
      elmnt.style.top = elmnt.offsetTop - pos2 + "px";
      elmnt.style.left = elmnt.offsetLeft - pos1 + "px";
    }

    function closeDragElement() {
      document.removeEventListener("mouseup", closeDragElement);
      document.removeEventListener("touchend", closeDragElement);
      document.removeEventListener("mousemove", elementDrag);
      document.removeEventListener("touchmove", elementDrag);
    }
  }

  // Source: https://github.com/hughsk/png-chunks-extract
  var uint8 = new Uint8Array(4);
  var int32 = new Int32Array(uint8.buffer);
  var uint32 = new Uint32Array(uint8.buffer);
  function extractChunks(data) {
    if (data[0] !== 0x89) throw new Error("Invalid .png file header");
    if (data[1] !== 0x50) throw new Error("Invalid .png file header");
    if (data[2] !== 0x4e) throw new Error("Invalid .png file header");
    if (data[3] !== 0x47) throw new Error("Invalid .png file header");
    if (data[4] !== 0x0d)
      throw new Error(
        "Invalid .png file header: possibly caused by DOS-Unix line ending conversion?"
      );
    if (data[5] !== 0x0a)
      throw new Error(
        "Invalid .png file header: possibly caused by DOS-Unix line ending conversion?"
      );
    if (data[6] !== 0x1a) throw new Error("Invalid .png file header");
    if (data[7] !== 0x0a)
      throw new Error(
        "Invalid .png file header: possibly caused by DOS-Unix line ending conversion?"
      );

    var ended = false;
    var chunks = [];
    var idx = 8;

    while (idx < data.length) {
      uint8[3] = data[idx++];
      uint8[2] = data[idx++];
      uint8[1] = data[idx++];
      uint8[0] = data[idx++];

      var length = uint32[0] + 4;
      var chunk = new Uint8Array(length);
      chunk[0] = data[idx++];
      chunk[1] = data[idx++];
      chunk[2] = data[idx++];
      chunk[3] = data[idx++];

      var name =
        String.fromCharCode(chunk[0]) +
        String.fromCharCode(chunk[1]) +
        String.fromCharCode(chunk[2]) +
        String.fromCharCode(chunk[3]);

      if (!chunks.length && name !== "IHDR") {
        throw new Error("IHDR header missing");
      }

      if (name === "IEND") {
        ended = true;
        chunks.push({ name: name, data: new Uint8Array(0) });
        break;
      }

      for (var i = 4; i < length; i++) {
        chunk[i] = data[idx++];
      }

      uint8[3] = data[idx++];
      uint8[2] = data[idx++];
      uint8[1] = data[idx++];
      uint8[0] = data[idx++];

      var crcActual = int32[0];
      var crcExpect = CRC32.buf(chunk);
      if (crcExpect !== crcActual) {
        throw new Error(
          "CRC values for " +
            name +
            " header do not match, PNG file is likely corrupted"
        );
      }

      var chunkData = new Uint8Array(chunk.buffer.slice(4));

      chunks.push({ name: name, data: chunkData });
    }

    if (!ended) {
      throw new Error(".png file ended prematurely: no IEND header was found");
    }

    return chunks;
  }
})();
