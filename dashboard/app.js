// ResolveeAI Super Admin Lifecycle Dashboard Logic

let fallbackEmployees = [
  {
    name: 'Algo',
    email: 'algo@vansshagarrwal.in',
    github_username: 'AlgorithmNodes',
    organization: 'ResolveeAI',
    role: 'SDE Intern',
    status: 'OFFBOARDED',
    permissions_summary: 'read-only to ResolveeAI/backend_api, strictly blocked from ResolveeAI/billing_core',
    aws_iam_user: 'resolvee-algo-intern',
    aws_access_key_id: 'AKIA6B45A73BF5EB',
    onboarded_at: '2026-09-26T09:29:12.596586+00:00',
    offboarded_at: '2026-09-26T10:08:54.486738+00:00',
    zero_trust_verified: true,
    exit_reason: 'Employee exit / contract end'
  }
];

let auditLogs = [
  {
    id: 'evt-201',
    time: '10:08 AM',
    action: 'OFFBOARD_COMPLETED',
    target: 'Algo (algo@vansshagarrwal.in)',
    policy: 'GitHub write revoked, IAM terminated, Zoho suspended',
    status: 'SUCCESS',
    danger: true
  },
  {
    id: 'evt-202',
    time: '09:29 AM',
    action: 'ONBOARD_COMPLETED',
    target: 'Algo (algo@vansshagarrwal.in)',
    policy: 'Daytona sandbox verified, RBAC applied, Zoho mailbox active',
    status: 'SUCCESS',
    danger: false
  }
];

let employees = [...fallbackEmployees];
let activeOffboardTarget = null;

// Notification Helper
function showToast(message, type = 'success') {
  const toastContainer = document.getElementById('toastContainer');
  if (!toastContainer) return;
  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.innerHTML = `<span>${type === 'success' ? '✓' : '⚠️'}</span><span>${message}</span>`;
  toastContainer.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 250);
  }, 4000);
}

// 1. DATA LOADING & RENDERING
async function loadData() {
  console.log('Loading employee data from /api/employees...');
  try {
    const res = await fetch('/api/employees');
    if (res.ok) {
      const data = await res.json();
      if (data.employees && data.employees.length > 0) {
        employees = data.employees;
        console.log('Loaded from API:', employees);
      }
    }
  } catch (err) {
    console.warn('API error, using active memory snapshot:', err);
  }

  updateMetrics();
  renderTable();
  renderAuditLogs();
}

function updateMetrics() {
  const total = employees.length;
  const active = employees.filter(e => e.status && e.status.toUpperCase().startsWith('ACTIVE')).length;
  const offboarded = employees.filter(e => e.status === 'OFFBOARDED').length;

  const statTotal = document.getElementById('statTotal');
  const statActive = document.getElementById('statActive');
  const statOffboarded = document.getElementById('statOffboarded');

  if (statTotal) statTotal.innerText = total;
  if (statActive) statActive.innerText = active;
  if (statOffboarded) statOffboarded.innerText = offboarded;

  const pipeInvited = document.getElementById('pipeInvited');
  const pipeZoho = document.getElementById('pipeZoho');
  const pipeDaytona = document.getElementById('pipeDaytona');
  const pipeActive = document.getElementById('pipeActive');
  const pipePendingOffboard = document.getElementById('pipePendingOffboard');
  const pipeRevoked = document.getElementById('pipeRevoked');

  if (pipeInvited) pipeInvited.innerText = 0;
  if (pipeZoho) pipeZoho.innerText = total;
  if (pipeDaytona) pipeDaytona.innerText = total;
  if (pipeActive) pipeActive.innerText = active;
  if (pipePendingOffboard) pipePendingOffboard.innerText = 0;
  if (pipeRevoked) pipeRevoked.innerText = offboarded;
}

function renderTable() {
  const employeeTableBody = document.getElementById('employeeTableBody');
  if (!employeeTableBody) return;

  const searchInput = document.getElementById('searchInput');
  const roleFilter = document.getElementById('roleFilter');
  const statusFilter = document.getElementById('statusFilter');

  const query = searchInput ? searchInput.value.toLowerCase().trim() : '';
  const selectedRole = roleFilter ? roleFilter.value : 'all';
  const selectedStatus = statusFilter ? statusFilter.value : 'all';

  const filtered = employees.filter(emp => {
    const matchesRole = selectedRole === 'all' || (emp.role && emp.role.toLowerCase() === selectedRole.toLowerCase());
    const matchesStatus = selectedStatus === 'all' || (selectedStatus === 'ACTIVE' ? (emp.status && emp.status.toUpperCase().startsWith('ACTIVE')) : (emp.status && emp.status.toUpperCase() === selectedStatus.toUpperCase()));
    
    const matchesSearch = 
      emp.name.toLowerCase().includes(query) ||
      (emp.email && emp.email.toLowerCase().includes(query)) ||
      (emp.github_username && emp.github_username.toLowerCase().includes(query)) ||
      (emp.role && emp.role.toLowerCase().includes(query));

    return matchesRole && matchesStatus && matchesSearch;
  });

  if (filtered.length === 0) {
    employeeTableBody.innerHTML = `
      <tr>
        <td colspan="7" style="text-align: center; color: var(--text-muted); padding: 32px;">
          No matching employee identities in directory.
        </td>
      </tr>
    `;
    return;
  }

  employeeTableBody.innerHTML = filtered.map(emp => {
    const isActive = Boolean(emp.status && emp.status.toUpperCase().startsWith('ACTIVE'));

    return `
      <tr>
        <td>
          <div class="emp-title">${emp.name}</div>
          <div class="emp-sub">Identity: ${emp.aws_iam_user || 'IAM Pending'}</div>
        </td>
        <td>
          <code>${emp.email || 'N/A'}</code>
        </td>
        <td>
          <span class="role-pill">${emp.role || 'SDE'}</span>
        </td>
        <td>
          <div style="font-weight: 600; color: #1E293B;">@${emp.github_username || 'N/A'}</div>
          <div style="font-size: 10px; color: var(--text-muted);">ResolveeAI / backend_api</div>
        </td>
        <td>
          <code>${emp.aws_access_key_id ? emp.aws_access_key_id.substring(0, 12) + '...' : 'REVOKED'}</code>
        </td>
        <td>
          <span class="badge ${isActive ? 'badge-green' : 'badge-rose'}">
            ${isActive ? 'ACTIVE' : 'OFFBOARDED'}
          </span>
        </td>
        <td style="text-align: right;">
          <div style="display: inline-flex; gap: 6px;">
            <button class="btn-row-action" onclick="openDetailModal('${emp.name}')">DETAILS</button>
            ${isActive ? `
              <button class="btn-row-action btn-row-offboard" onclick="openOffboardPrompt('${emp.name}')">
                OFFBOARD
              </button>
            ` : `
              <span style="font-size: 11px; color: var(--text-muted); padding: 4px 6px;">TERMINATED</span>
            `}
          </div>
        </td>
      </tr>
    `;
  }).join('');
}

function renderAuditLogs() {
  const auditTableBody = document.getElementById('auditTableBody');
  if (!auditTableBody) return;

  auditTableBody.innerHTML = auditLogs.map(log => `
    <tr>
      <td><code>${log.time}</code></td>
      <td><strong>${log.action}</strong></td>
      <td>${log.target}</td>
      <td style="font-size: 11px; color: var(--text-secondary);">${log.policy}</td>
      <td>
        <span class="badge ${log.danger ? 'badge-rose' : 'badge-green'}">
          ${log.status}
        </span>
      </td>
    </tr>
  `).join('');
}

// 2. CONVERSATIONAL CHAT DRAWER LOGIC
function openChatDrawer(initialText = '') {
  const chatDrawerOverlay = document.getElementById('chatDrawerOverlay');
  const chatInput = document.getElementById('chatInput');
  if (chatDrawerOverlay) chatDrawerOverlay.classList.add('open');
  if (chatInput) {
    if (initialText) chatInput.value = initialText;
    chatInput.focus();
  }
}

function closeChatDrawer() {
  const chatDrawerOverlay = document.getElementById('chatDrawerOverlay');
  if (chatDrawerOverlay) chatDrawerOverlay.classList.remove('open');
}

window.sendQuickPrompt = function(promptText) {
  const chatInput = document.getElementById('chatInput');
  if (chatInput) chatInput.value = promptText;
  handleChatSubmit();
};

function appendMessage(text, isUser = false, toolCalls = []) {
  const chatMessages = document.getElementById('chatMessages');
  if (!chatMessages) return;

  const msgEl = document.createElement('div');
  msgEl.className = `msg ${isUser ? 'msg-user' : 'msg-agent'}`;

  let formattedText = text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br/>');

  let toolsHtml = '';
  if (toolCalls && toolCalls.length > 0) {
    toolsHtml = `
      <div class="tool-badge-box">
        ${toolCalls.map(t => `<span class="tool-badge">⚙️ ${t}</span>`).join('')}
      </div>
    `;
  }

  msgEl.innerHTML = `
    <div class="msg-avatar">${isUser ? '👤' : '🤖'}</div>
    <div class="msg-bubble">
      <div>${formattedText}</div>
      ${toolsHtml}
    </div>
  `;

  chatMessages.appendChild(msgEl);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function handleChatSubmit(e) {
  if (e) e.preventDefault();
  const chatInput = document.getElementById('chatInput');
  const chatMessages = document.getElementById('chatMessages');
  if (!chatInput) return;

  const text = chatInput.value.trim();
  if (!text) return;

  appendMessage(text, true);
  chatInput.value = '';

  const typingEl = document.createElement('div');
  typingEl.className = 'msg msg-agent';
  typingEl.id = 'agentTyping';
  typingEl.innerHTML = `
    <div class="msg-avatar">🤖</div>
    <div class="msg-bubble" style="color: var(--text-secondary); font-style: italic;">
      TrueForge is evaluating policy & tools...
    </div>
  `;
  if (chatMessages) {
    chatMessages.appendChild(typingEl);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text, session_id: 'dashboard-session' })
    });

    if (typingEl) typingEl.remove();

    if (res.ok) {
      const data = await res.json();
      appendMessage(data.reply, false, data.tool_calls || []);

      if (data.action_completed) {
        showToast('Directory & Pipeline Updated in Real-Time');
        loadData();
      }
    } else {
      appendMessage('⚠️ Error communicating with TrueForge backend API.', false);
    }
  } catch (err) {
    if (typingEl) typingEl.remove();
    handleLocalChatFallback(text);
  }
}

function handleLocalChatFallback(text) {
  const lower = text.toLowerCase();
  if (lower.includes('offboard')) {
    appendMessage("⚠️ **Disambiguation Guard:** Which employee would you like to offboard? Please confirm their exact corporate email (`@vansshagarrwal.in`).", false);
  } else if (lower.includes('onboard') || lower.includes('profile')) {
    appendMessage("I'm ready to provision the profile! Please provide: 1) Full Name, 2) Role, 3) GitHub username, 4) Personal delivery email for AWS credentials.", false);
  } else {
    appendMessage("👋 I am TrueForge, your autonomous lifecycle agent. Ask me to *'Onboard Alex as SDE'* or *'Offboard Algo'* to see conversational zero-trust actions.", false);
  }
}

// 3. TABLE ACTIONS & MODALS
window.openOffboardPrompt = function(employeeName) {
  openChatDrawer(`Offboard ${employeeName}`);
};

window.openDetailModal = function(employeeName) {
  const emp = employees.find(e => e.name.toLowerCase() === employeeName.toLowerCase());
  if (!emp) return;

  const detailName = document.getElementById('detailName');
  const detailEmail = document.getElementById('detailEmail');
  const detailContent = document.getElementById('detailContent');
  const detailModal = document.getElementById('detailModal');

  if (detailName) detailName.innerText = `${emp.name} • Audit Details`;
  if (detailEmail) detailEmail.innerText = emp.email || 'N/A';

  if (detailContent) {
    detailContent.innerHTML = `
      <div class="detail-grid">
        <div class="detail-box">
          <label>LIFECYCLE STATUS</label>
          <span style="color: ${emp.status === 'ACTIVE' ? '#059669' : '#E11D48'};">
            ${emp.status || 'UNKNOWN'}
          </span>
        </div>
        <div class="detail-box">
          <label>ASSIGNED ROLE</label>
          <span>${emp.role || 'SDE'}</span>
        </div>
        <div class="detail-box">
          <label>GITHUB IDENTITY</label>
          <span>@${emp.github_username || 'N/A'}</span>
        </div>
        <div class="detail-box">
          <label>AWS IAM USER</label>
          <span>${emp.aws_iam_user || 'N/A'}</span>
        </div>
        <div class="detail-box">
          <label>PROVISIONED TIMESTAMP</label>
          <span>${emp.onboarded_at ? new Date(emp.onboarded_at).toLocaleString() : 'N/A'}</span>
        </div>
        <div class="detail-box">
          <label>OFFBOARDED TIMESTAMP</label>
          <span>${emp.offboarded_at ? new Date(emp.offboarded_at).toLocaleString() : 'Active in Perimeter'}</span>
        </div>
      </div>

      <div class="detail-box" style="margin-bottom: 12px;">
        <label>ZERO-TRUST RBAC POLICY</label>
        <span style="font-size: 11px; color: var(--text-secondary);">${emp.permissions_summary || 'Standard developer isolation policy.'}</span>
      </div>

      <div class="secret-shield-box">
        <strong>Zero-Knowledge Delivery Protocol:</strong>
        <div style="font-size: 11px; margin-top: 2px;">
          AWS Secret Access Key was generated and immediately dispatched encrypted to the candidate's verified personal inbox. Plaintext secret is never logged or exposed in the operations console.
        </div>
      </div>
    `;
  }

  if (detailModal) detailModal.classList.add('open');
};

const closeModals = () => {
  const onboardModal = document.getElementById('onboardModal');
  const offboardModal = document.getElementById('offboardModal');
  const detailModal = document.getElementById('detailModal');
  if (onboardModal) onboardModal.classList.remove('open');
  if (offboardModal) offboardModal.classList.remove('open');
  if (detailModal) detailModal.classList.remove('open');
};

// 4. ATTACH ALL EVENT LISTENERS SAFELY
document.addEventListener('DOMContentLoaded', () => {
  console.log('Initializing ResolveeAI SuperAdmin Dashboard...');
  loadData();

  // Search & Filter listeners
  const applyFiltersBtn = document.getElementById('applyFiltersBtn');
  const searchInput = document.getElementById('searchInput');
  const roleFilter = document.getElementById('roleFilter');
  const statusFilter = document.getElementById('statusFilter');
  const refreshBtn = document.getElementById('refreshBtn');

  if (applyFiltersBtn) applyFiltersBtn.addEventListener('click', renderTable);
  if (searchInput) searchInput.addEventListener('input', renderTable);
  if (roleFilter) roleFilter.addEventListener('change', renderTable);
  if (statusFilter) statusFilter.addEventListener('change', renderTable);

  if (refreshBtn) {
    refreshBtn.addEventListener('click', async () => {
      await loadData();
      showToast('Synced with MongoDB Atlas & TrueForge Agent');
    });
  }

  // Chat Drawer buttons
  const floatingChatBtn = document.getElementById('floatingChatBtn');
  const openChatBtn = document.getElementById('openChatBtn');
  const closeChatDrawerBtn = document.getElementById('closeChatDrawerBtn');
  const chatDrawerOverlay = document.getElementById('chatDrawerOverlay');
  const chatForm = document.getElementById('chatForm');

  if (floatingChatBtn) floatingChatBtn.addEventListener('click', () => openChatDrawer());
  if (openChatBtn) openChatBtn.addEventListener('click', () => openChatDrawer());
  if (closeChatDrawerBtn) closeChatDrawerBtn.addEventListener('click', closeChatDrawer);

  if (chatDrawerOverlay) {
    chatDrawerOverlay.addEventListener('click', (e) => {
      if (e.target === chatDrawerOverlay) closeChatDrawer();
    });
  }

  if (chatForm) chatForm.addEventListener('submit', handleChatSubmit);

  // Close modals
  const closeDetailModal = document.getElementById('closeDetailModal');
  const closeDetailBtn = document.getElementById('closeDetailBtn');
  if (closeDetailModal) closeDetailModal.addEventListener('click', closeModals);
  if (closeDetailBtn) closeDetailBtn.addEventListener('click', closeModals);
});

// Immediate execution fallback
loadData();
