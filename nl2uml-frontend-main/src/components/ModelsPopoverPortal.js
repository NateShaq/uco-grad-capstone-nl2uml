import { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';

/**
 * Mounts children into a body-level portal so the popover can escape overflow/stacking contexts.
 */
export default function ModelsPopoverPortal({ children }) {
  const [container] = useState(() => {
    const node = document.createElement('div');
    node.setAttribute('data-portal', 'models-popover');
    node.style.position = 'relative';
    node.style.zIndex = 999997;
    return node;
  });

  useEffect(() => {
    document.body.appendChild(container);
    return () => {
      document.body.removeChild(container);
    };
  }, [container]);

  return createPortal(children, container);
}
