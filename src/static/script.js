function flowBit() {
  return {
    darkMode: JSON.parse(localStorage.getItem('darkMode')) || false,
    taskList: [],
    newTask: {
      content: '',
      startTime: '',
      endTime: '',
      days: []
    },
    taskToEdit: {
      id: null,
      content: '',
      startTime: '',
      endTime: '',
      days: []
    },
    selectedTasks: [],
    filter: ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'][new Date().getDay()],
    showAddModal: false,
    showEditModal: false,

    async init() {
      await this.loadTasks();
    },

    toggleDarkMode() {
      this.darkMode = !this.darkMode;
      localStorage.setItem('darkMode', JSON.stringify(this.darkMode));
    },

    async loadTasks() {
      const res = await fetch('/tasks');
      const data = await res.json();
      
      this.taskList = data.map(task => ({
        id: task.id,
        content: task.title,
        startTime: task.start_date.slice(11, 16),
        endTime: task.end_date.slice(11, 16),
        days: task.days,
        user_id: task.user_id
      }));
      console.log("Tarefas carregadas:", this.taskList);
    },

    get sortedTaskList() {
      return this.taskList
        .slice()
        .sort((a, b) => (a.startTime || '').localeCompare(b.startTime || ''));
    },

  async addTask() {
    if (this.newTask.content.trim() === '' || this.newTask.days.length === 0) {
      alert('Preencha todos os campos obrigatórios.');
      return;
    }

    if (this.newTask.startTime > this.newTask.endTime) {
      alert('O horário de início não pode ser maior que o de término.');
      return;
    }

    const today = new Date().toISOString().slice(0, 10);

    const payload = {
      title: this.newTask.content,
      description: '',
      status: '',
      start_date: `${today}T${this.newTask.startTime}:00`,
      end_date: `${today}T${this.newTask.endTime}:00`,
      days: this.newTask.days,
      done: false,
      user_id: 1
    };

    const res = await fetch('/tasks', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      const err = await res.json();
      alert('Erro ao adicionar tarefa: ' + (err.detail || res.statusText));
      return;
    }

    this.newTask = { content: '', startTime: '', endTime: '', days: [] };
    this.showAddModal = false;
    await this.loadTasks();
  },


    async removeTasks() {
      for (let id of this.selectedTasks) {
        await fetch(`/tasks/${id}`, { method: 'DELETE' });
      }
      this.selectedTasks = [];
      await this.loadTasks();
    },

    toggleSelection(id) {
      const index = this.selectedTasks.indexOf(id);
      if (index >= 0) this.selectedTasks.splice(index, 1);
      else this.selectedTasks.push(id);
    },

    openEditModal(task) {
      this.taskToEdit = { ...task };
      this.showEditModal = true;
    },


  async editTask() {
    if (this.taskToEdit.content.trim() === '') {
      alert('O conteúdo da tarefa não pode estar vazio.');
      return;
    }

    if (this.taskToEdit.days.length === 0) {
      alert('Você deve selecionar pelo menos um dia.');
      return;
    }

    if (this.taskToEdit.startTime > this.taskToEdit.endTime) {
      alert('O horário de início não pode ser maior que o horário de término.');
      return;
    }
    const today = new Date().toISOString().slice(0, 10);
    const payload = {
      title: this.taskToEdit.content,
      description: '',      
      status: '',             
      start_date: `${today}T${this.taskToEdit.startTime}:00`,
      end_date: `${today}T${this.taskToEdit.endTime}:00`,
      days: this.taskToEdit.days,
      done: false,
      user_id: this.taskToEdit.user_id
    };

    try {
      const response = await fetch(`/tasks/${this.taskToEdit.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Erro ao atualizar tarefa');
      }

      this.showEditModal = false;
      await this.loadTasks();
    } catch (error) {
      alert(`Erro: ${error.message}`);
    }
  }
  };
}



