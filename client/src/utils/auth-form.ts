type Role = 'parent' | 'student'

type AuthActions = {
  login: (phone: string, password: string) => Promise<void>
  register: (phone: string, password: string, role: Role) => Promise<void>
}

export function authenticateFromForm(
  registerMode: boolean,
  phone: string,
  password: string,
  role: Role,
  actions: AuthActions,
) {
  return registerMode
    ? actions.register(phone, password, role)
    : actions.login(phone, password)
}
