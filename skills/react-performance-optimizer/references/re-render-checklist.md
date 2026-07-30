# React Re-Render Audit Checklist

Use these specific code patterns when refactoring complex React component trees:

### Context Splitting Pattern

**Bad (Single Context Causes All Consumers to Re-render):**

```tsx
const UserContext = createContext<{
  user: User;
  setUser: (u: User) => void;
} | null>(null);
```

**Good (Separate Data from Mutator):**

```tsx
const UserStateContext = createContext<User null |>(null);
const UserDispatchContext = createContext<((u: User) => void) | null>(null);

export const UserProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<User null |>(null);
  return (
    <UserStateContext.Provider value="{user}">
      <UserDispatchContext.Provider value="{setUser}">
        {children}
      </UserDispatchContext.Provider>
    </UserStateContext.Provider>
  );
};
```

**Object Reference Stability Check**

- Check inline object literals inside JSX props:
  - Bad: style={{ marginTop: 10 }} -> Instantiates new object reference every render.

  - Bad: onClick={() => handleClick(id)} -> Instantiates new closure every render. Pass id inside child or wrap with useCallback.
