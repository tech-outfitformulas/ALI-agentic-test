import json
from typing import Any, List, Sequence, Tuple, Optional
from langgraph.store.base import BaseStore, Item, Op, PutOp, GetOp, SearchOp, ListNamespacesOp
from ..core.firebase import db

class FirestoreStore(BaseStore):
    def __init__(self, collection_name: str = "memory"):
        self.collection = db.collection(collection_name)

    def _get_doc_id(self, namespace: Tuple[str, ...], key: str) -> str:
        # Create a unique ID from namespace and key
        ns_str = ":".join(namespace)
        return f"{ns_str}::{key}"

    def batch(self, ops: Sequence[Op]) -> List[Any]:
        results = []
        batch = db.batch()
        
        for op in ops:
            if isinstance(op, PutOp):
                doc_id = self._get_doc_id(op.namespace, op.key)
                doc_ref = self.collection.document(doc_id)
                data = {
                    "value": op.value,
                    "namespace": op.namespace,
                    "key": op.key,
                    "updated_at": firestore.SERVER_TIMESTAMP
                }
                batch.set(doc_ref, data, merge=True)
                results.append(None)
                
            elif isinstance(op, GetOp):
                doc_id = self._get_doc_id(op.namespace, op.key)
                doc_ref = self.collection.document(doc_id)
                doc = doc_ref.get()
                if doc.exists:
                    data = doc.to_dict()
                    results.append(Item(
                        value=data.get("value"),
                        key=data.get("key"),
                        namespace=tuple(data.get("namespace", [])),
                        created_at=data.get("created_at"), 
                        updated_at=data.get("updated_at")
                    ))
                else:
                    results.append(None)
                    
            elif isinstance(op, SearchOp):
                # Simplified search: exact match on namespace
                query = self.collection.where("namespace", "==", list(op.namespace))
                docs = query.stream()
                items = []
                for doc in docs:
                    data = doc.to_dict()
                    items.append(Item(
                        value=data.get("value"),
                        key=data.get("key"),
                        namespace=tuple(data.get("namespace", [])),
                        created_at=data.get("created_at"),
                        updated_at=data.get("updated_at")
                    ))
                results.append(items)
                
            elif isinstance(op, ListNamespacesOp):
                results.append([])

        # Commit writes
        batch.commit()
        return results

        # Commit writes
        batch.commit()
        return results

    async def abatch(self, ops: Sequence[Op]) -> List[Any]:
        return self.batch(ops)

# Need to import firestore for SERVER_TIMESTAMP
from firebase_admin import firestore
